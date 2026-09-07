"""Real MCP transport test; --live additionally requests real YouTube acquisition."""
import argparse
import asyncio
import json
import time
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main(url, live):
    if urlsplit(url).hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("This smoke test is for the local MCP endpoint only")
    def local_client(**kwargs):
        return httpx.AsyncClient(**kwargs, trust_env=False)
    async with streamablehttp_client(url, httpx_client_factory=local_client) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()
            tools = {t.name: t for t in listing.tools}
            assert set(tools) == {"search", "fetch", "acquire_audio", "job_status", "analyze_audio"}
            assert tools["search"].annotations.readOnlyHint
            assert tools["fetch"].annotations.readOnlyHint
            assert not tools["acquire_audio"].annotations.readOnlyHint
            print(json.dumps({"mcp_initialize": "passed", "tools": sorted(tools)}, ensure_ascii=False), flush=True)
            invalid = await session.call_tool("fetch", {"id": "../etc/passwd"})
            assert invalid.isError
            print(json.dumps({"invalid_id_rejected": True}), flush=True)
            if not live:
                return
            result = await session.call_tool("acquire_audio", {
                "video_id": "mdhtm6qjmhU", "expected_channel_id": "UCBUAlfIrcw1f0c4qGrYn3xA",
                "request_key": "live-" + str(time.time_ns()),
            })
            if result.isError:
                raise RuntimeError("MCP acquisition call failed: " + str(result.content))
            job = result.structuredContent
            print(json.dumps({"job_started": job}, ensure_ascii=False), flush=True)
            deadline = time.monotonic() + 210
            while time.monotonic() < deadline:
                result = await session.call_tool("job_status", {"job_id": job["job_id"]})
                status = result.structuredContent
                if status["status"] not in ("queued", "running"):
                    print(json.dumps({"live_result": status}, ensure_ascii=False), flush=True)
                    return
                await asyncio.sleep(2)
            raise TimeoutError("live MCP job exceeded test deadline")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8841/mcp")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--spawn", action="store_true", help="Run server and client in the same local network namespace")
    args = parser.parse_args()
    if args.spawn:
        with tempfile.TemporaryDirectory(prefix="smoke-", dir=Path(__file__).parent) as data:
            proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name("server.py")),
                                     "--transport", "streamable-http", "--data-dir", data],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                for _ in range(100):
                    if proc.poll() is not None:
                        raise RuntimeError("server failed to start")
                    try:
                        with socket.create_connection(("127.0.0.1", 8841), timeout=0.1):
                            break
                    except OSError:
                        time.sleep(0.05)
                asyncio.run(main("http://127.0.0.1:8841/mcp", args.live))
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=190)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
    else:
        asyncio.run(main(args.url, args.live))
