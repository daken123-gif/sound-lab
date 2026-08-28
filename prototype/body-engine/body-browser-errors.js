export class BodyBrowserSessionError extends Error {
  constructor(phase, cause) {
    const message = cause instanceof Error ? cause.message : String(cause);
    super(message);
    this.name = "BodyBrowserSessionError";
    this.phase = phase;
    this.causeName = cause instanceof Error ? cause.name : "Error";
    this.cause = cause;
  }
}

export function classifyBodyBrowserFailure(error, { secureContext = true } = {}) {
  const phase = error?.phase ?? "preflight";
  const name = error?.causeName ?? error?.name ?? "Error";
  const message = error instanceof Error ? error.message : String(error);

  let code = "START_FAILED";
  if (!secureContext) code = "INSECURE_CONTEXT";
  else if (name === "AudioContextUnavailableError") code = "AUDIO_CONTEXT_UNAVAILABLE";
  else if (name === "MediaDevicesUnavailableError") code = "MEDIA_DEVICES_UNAVAILABLE";
  else if (name === "AudioWorkletUnavailableError") code = "AUDIO_WORKLET_UNAVAILABLE";
  else if (phase === "worklet") code = "WORKLET_LOAD_FAILED";
  else if (name === "NotAllowedError") code = "MIC_PERMISSION_DENIED";
  else if (name === "NotFoundError") code = "MIC_NOT_FOUND";
  else if (name === "NotReadableError" || name === "AbortError") code = "MIC_UNAVAILABLE";
  else if (name === "OverconstrainedError") code = "MIC_CONSTRAINT_FAILED";
  else if (name === "SecurityError") code = "MIC_SECURITY_BLOCKED";

  return { state: "failed", code, phase, name, message };
}
