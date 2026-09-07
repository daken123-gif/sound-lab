#!/usr/bin/env python3
"""Offline onset evaluation. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
from array import array
import hashlib
import html
import json
import math
from pathlib import Path
import re
import statistics
import sys

VERSION = "0.1.0"
MAX_CELLS = 2_000_000


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label}: 有限の数値が必要です")
    return float(value)


def scope(value):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("scope_seconds: [開始秒, 終了秒] が必要です")
    start, end = [number(x, "scope_seconds") for x in value]
    if start < 0 or end <= start:
        raise ValueError("scope_seconds: 0 <= 開始 < 終了 が必要です")
    return start, end


def times(value, bounds):
    if not isinstance(value, list):
        raise ValueError("打点は秒単位の配列にしてください")
    result = [number(x, "打点時刻") for x in value]
    if any(x < bounds[0] or x >= bounds[1] for x in result):
        raise ValueError("打点が指定区間 [開始, 終了) の外にあります")
    if any(a > b for a, b in zip(result, result[1:])):
        raise ValueError("打点を時刻順にしてください（重複は消さずに評価します）")
    return result


def source_hash(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("source_sha256: 小文字16進数64桁が必要です")
    return value


def load(path):
    raw = Path(path).read_bytes()
    if len(raw) > 20_000_000:
        raise ValueError("入力が20MBを超えています。区間を分割してください")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("入力の最上位はJSONオブジェクトにしてください")
    return value, hashlib.sha256(raw).hexdigest()


def document(value):
    if value.get("schema_version") != 1:
        raise ValueError("schema_version は 1 が必要です")
    bounds = scope(value.get("scope_seconds"))
    source_hash(value.get("source_sha256"))
    if value.get("reference_kind") not in {"known_events", "human_annotations", "candidate"}:
        raise ValueError("reference_kind: known_events / human_annotations / candidate が必要です")
    if not isinstance(value.get("provenance"), str) or not value["provenance"].strip():
        raise ValueError("provenance に作成方法・由来を記載してください")
    return times(value.get("onsets_seconds"), bounds)


def match(reference, estimate, tolerance_s):
    """Maximize monotone one-to-one matches, then minimize absolute timing error.

    No clock alignment or quantization. Duplicate estimates consume separate slots.
    O(n*m) time, byte-per-cell traceback; refuse oversized requests explicitly.
    """
    tolerance_s = number(tolerance_s, "許容差")
    if tolerance_s <= 0:
        raise ValueError("許容差は正数にしてください")
    n, m = len(reference), len(estimate)
    if n * m > MAX_CELLS:
        raise ValueError("照合が大きすぎます。共通区間を短く切って比較してください")
    trace = bytearray((n + 1) * (m + 1))
    prev_n, prev_e = array("I", [0]) * (m + 1), array("d", [0.0]) * (m + 1)
    for i, r in enumerate(reference, 1):
        curr_n, curr_e = array("I", [0]) * (m + 1), array("d", [0.0]) * (m + 1)
        for j, e in enumerate(estimate, 1):
            count, error, action = prev_n[j], prev_e[j], 1
            if (curr_n[j-1], -curr_e[j-1]) > (count, -error):
                count, error, action = curr_n[j-1], curr_e[j-1], 2
            delta = abs(e - r)
            if delta <= tolerance_s + 1e-12:
                candidate = (prev_n[j-1] + 1, prev_e[j-1] + delta)
                if (candidate[0], -candidate[1]) > (count, -error):
                    count, error, action = candidate[0], candidate[1], 3
            curr_n[j], curr_e[j] = count, error
            trace[i * (m + 1) + j] = action
        prev_n, prev_e = curr_n, curr_e
    i, j, pairs = n, m, []
    while i and j:
        action = trace[i * (m + 1) + j]
        if action == 3:
            pairs.append((i-1, j-1))
            i, j = i-1, j-1
        elif action == 1:
            i -= 1
        else:
            j -= 1
    return list(reversed(pairs))


def compare(reference, estimate, tolerance_ms, accuracy=False):
    pairs = match(reference, estimate, tolerance_ms / 1000)
    ri, ei = {i for i, _ in pairs}, {j for _, j in pairs}
    errors = [(estimate[j] - reference[i]) * 1000 for i, j in pairs]
    n, m, k = len(reference), len(estimate), len(pairs)
    metrics = {"reference_events": n, "estimate_events": m, "matched_events": k}
    if accuracy:
        metrics.update(precision=k/m if m else None, recall=k/n if n else None,
                       f1=2*k/(n+m) if n+m else None)
    else:
        metrics["agreement_f1_not_accuracy"] = 2*k/(n+m) if n+m else None
    metrics.update(median_signed_error_ms=statistics.median(errors) if errors else None,
                   max_abs_error_ms_matched_only=max(map(abs, errors)) if errors else None)
    return {"status": "measured" if n else "no_reference_events",
            "mode": "reference_accuracy" if accuracy else "candidate_agreement_not_accuracy",
            "tolerance_ms": tolerance_ms, "metrics": metrics,
            "reference_only_seconds": [v for i, v in enumerate(reference) if i not in ri],
            "estimate_only_seconds": [v for j, v in enumerate(estimate) if j not in ei],
            "matches": [{"reference_s": reference[i], "estimate_s": estimate[j],
                         "signed_error_ms": (estimate[j]-reference[i])*1000} for i,j in pairs]}


def compare_documents(a, b, tolerance_ms):
    ref, est = document(a), document(b)
    if a["source_sha256"] != b["source_sha256"]:
        raise ValueError("音源hashが異なります。版・時刻対応を確認してから比較してください")
    if a["scope_seconds"] != b["scope_seconds"]:
        raise ValueError("区間が異なります。共通区間を明示した入力を作成してください")
    return {"source_sha256": a["source_sha256"], "scope_seconds": a["scope_seconds"],
            "reference_kind": a["reference_kind"],
            "reference_provenance": a["provenance"], "estimate_provenance": b["provenance"],
            "reference_authority": "input_declaration_not_independently_verified",
            **compare(ref, est, tolerance_ms, a["reference_kind"] != "candidate")}


def window_audit(value, tolerance_ms=15, short_s=10, long_s=30, edge_s=.1):
    source_hash(value.get("source_sha256"))
    outer = scope(value.get("scope_seconds"))
    for v in (short_s, long_s, edge_s):
        number(v, "窓設定")
    if not (0 < short_s < long_s and 0 <= edge_s < short_s/2):
        raise ValueError("窓は 0 < 短窓 < 長窓、端除外は短窓の半分未満にしてください")
    rows = value.get("windows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("windows がありません")
    checked, seen = [], set()
    for row in rows:
        bounds = scope([row.get("start_s"), row.get("end_s")])
        if bounds in seen or bounds[0] < outer[0] or bounds[1] > outer[1]:
            raise ValueError("窓の重複または外側区間からの逸脱があります")
        seen.add(bounds)
        checked.append((bounds, times(row.get("onset_candidates_absolute_s"), bounds)))
    reports, skipped = [], []
    for (start, end), short in checked:
        if not math.isclose(end-start, short_s, abs_tol=1e-9):
            continue
        long = next((ts for (s,e),ts in checked if s == start and math.isclose(e-s,long_s,abs_tol=1e-9)), None)
        if long is None:
            skipped.append({"start_s": start, "reason": "same_start_long_window_missing"})
            continue
        low, high = start+edge_s, end-edge_s
        ref = [t for t in short if low <= t < high]
        est = [t for t in long if low <= t < high]
        reports.append({"scope_seconds": [low, high], **compare(ref, est, tolerance_ms)})
    if not reports:
        raise ValueError("同じ開始時刻の短窓・長窓の組がありません")
    return {"mode": "window_sensitivity_not_accuracy", "source_sha256": value["source_sha256"],
            "scope_seconds": list(outer), "short_window_s": short_s, "long_window_s": long_s,
            "edge_exclusion_s": edge_s, "compared_pairs": len(reports),
            "skipped_short_windows": skipped, "comparisons": reports,
            "extractor_sha256_declared": value.get("extractor_sha256")}


def render(report):
    comparisons = report.get("comparisons", [report])
    sections = []
    overview = ["<h2>食い違いの多い区間</h2><p>重なる窓を含むため、件数を合計して曲全体の誤り数にしないでください。</p><ul>"]
    ranked = sorted(enumerate(comparisons), key=lambda item: -(len(item[1]["reference_only_seconds"])+len(item[1]["estimate_only_seconds"])))
    for index, c in ranked:
        count = len(c["reference_only_seconds"])+len(c["estimate_only_seconds"])
        overview.append(f"<li><a href='#pair-{index}'>"+html.escape(str(c.get("scope_seconds","入力区間")))+f"</a>：片側だけの候補 {count} 件</li>")
    overview.append("</ul>")
    for index, c in enumerate(comparisons):
        metrics = c["metrics"]
        sections.append(f"<section id='pair-{index}'><h2>区間 " + html.escape(str(c.get("scope_seconds", "入力区間"))) + "</h2>")
        sections.append("<p>一致打点: %s ／ 左: %s ／ 右: %s</p>" %
                        (metrics["matched_events"], metrics["reference_events"], metrics["estimate_events"]))
        sections.append("<table><tr><th>確認する時刻（秒）</th><th>状態</th></tr>")
        for key, label in [("reference_only_seconds", "左だけ：正解参照の場合は見逃し候補"),
                           ("estimate_only_seconds", "右だけ：正解参照の場合は余計な検出候補")]:
            for t in c[key]:
                sections.append(f"<tr><td>{t:.6f}</td><td>{label}</td></tr>")
        sections.append("</table></section>")
    return ("<!doctype html><html lang='ja'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            "<title>採譜用 打点検証</title><style>body{max-width:960px;margin:2em auto;padding:0 1em;font:16px system-ui;line-height:1.6}"
            "td,th{border:1px solid #aaa;padding:.4em}table{border-collapse:collapse}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>"
            "<h1>採譜用 打点検証</h1><p>方式間の一致は正解率ではありません。時刻は音源先頭からの秒数です。"
            "自動量子化・時刻補正・音源取得・採譜は行っていません。</p>" + "".join(overview) + "".join(sections) +
            "<details><summary>全測定値・入力由来・対応打点</summary><pre>" +
            html.escape(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)) + "</pre></details></html>")


def main(argv=None):
    parser = argparse.ArgumentParser(description="採譜用の打点照合。音声や外部ライブラリなしで実行できます。")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("compare", help="正解打点または別方式の候補打点と比較")
    p.add_argument("reference"); p.add_argument("estimate")
    w = sub.add_parser("windows", help="Jeff Mills形式の窓別打点JSONを直接検査")
    w.add_argument("input"); w.add_argument("--short-s", type=float, default=10)
    w.add_argument("--long-s", type=float, default=30); w.add_argument("--edge-s", type=float, default=.1)
    for command in (p, w):
        command.add_argument("--tolerance-ms", type=float, default=15)
        command.add_argument("--output-dir", required=True, help="新規ディレクトリ。既存結果は上書きしません")
    args = parser.parse_args(argv)
    try:
        tolerance = number(args.tolerance_ms, "許容差")
        if tolerance <= 0:
            raise ValueError("許容差は正数にしてください")
        if args.command == "compare":
            a, ah = load(args.reference); b, bh = load(args.estimate)
            report = compare_documents(a,b,tolerance)
            inputs = [{"name": Path(args.reference).name, "sha256": ah}, {"name": Path(args.estimate).name, "sha256": bh}]
        else:
            value, digest = load(args.input)
            report = window_audit(value,tolerance,args.short_s,args.long_s,args.edge_s)
            inputs = [{"name": Path(args.input).name, "sha256": digest}]
        report.update(tool_version=VERSION, tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      inputs=inputs, alignment="none", quantization="none",
                      limitation="音源hash・参照の権威は入力の申告。音声との照合、楽器・音高・音色の検証は未実施。")
        encoded = json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False) + "\n"
        page = render(report)
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=False)
        (output/"report.json").write_text(encoded,encoding="utf-8")
        (output/"report.html").write_text(page,encoding="utf-8")
        if json.loads((output/"report.json").read_text(encoding="utf-8")) != report:
            raise ValueError("出力の読戻しが一致しません")
        print(f"検査完了: {output}/report.html と report.json（採譜精度の合格宣言ではありません）")
        return 0
    except (ValueError, OSError, TypeError, KeyError, AttributeError) as exc:
        print(f"検査できません: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
