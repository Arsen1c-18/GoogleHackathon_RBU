export type VoiceLang = "en" | "hi";

export const VOICE_LANGS: { code: VoiceLang; label: string; bcp47: string }[] = [
  { code: "en", label: "English", bcp47: "en-IN" },
  { code: "hi", label: "हिन्दी", bcp47: "hi-IN" },
];

export function normalizeVoiceLang(lang: string): VoiceLang {
  return lang.startsWith("hi") ? "hi" : "en";
}

/** Browser TTS readback for zero-typing confirmation. No server cost. */
export function speak(text: string, lang: VoiceLang): void {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
  const synth = window.speechSynthesis;
  synth.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  const target = lang === "hi" ? "hi-IN" : "en-IN";
  const voice =
    synth.getVoices().find((v) => v.lang === target) ??
    synth.getVoices().find((v) => v.lang.startsWith(lang));
  if (voice) utter.voice = voice;
  utter.lang = voice?.lang ?? target;
  synth.speak(utter);
}

export type TranscribeResult = {
  text: string;
  provider: string;
  language: VoiceLang;
};

export async function transcribeAudio(
  blob: Blob,
  lang: VoiceLang,
  getIdToken?: () => Promise<string | null>
): Promise<TranscribeResult> {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const form = new FormData();
  form.append("file", blob, "complaint.webm");
  form.append("language", lang);
  const headers: HeadersInit = {};
  if (getIdToken) {
    const token = await getIdToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${apiUrl}/api/voice/transcribe`, {
    method: "POST",
    headers,
    body: form,
  });
  if (!res.ok) throw new Error(`Transcribe failed: ${res.status}`);
  return res.json() as Promise<TranscribeResult>;
}

/** Record mic audio with silence-friendly manual stop. Returns webm Blob. */
export function recordMic(
  onLevel?: (level: number) => void
): Promise<{ stop: () => Promise<Blob>; stream: MediaStream }> {
  return (async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream, {
      mimeType: MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : undefined,
    });
    const chunks: Blob[] = [];
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    // Optional live level meter for UI feedback
    let raf = 0;
    if (onLevel) {
      const ctx = new AudioContext();
      const src = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      src.connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteFrequencyData(data);
        const avg =
          data.reduce((a, b) => a + b, 0) / Math.max(1, data.length) / 255;
        onLevel(avg);
        raf = requestAnimationFrame(tick);
      };
      tick();
      recorder.onstop = () => {
        cancelAnimationFrame(raf);
        void ctx.close().catch(() => {});
      };
    }
    recorder.start();
    return {
      stream,
      stop: () =>
        new Promise<Blob>((resolve) => {
          recorder.onstop = () => {
            stream.getTracks().forEach((t) => t.stop());
            resolve(new Blob(chunks, { type: "audio/webm" }));
          };
          recorder.stop();
        }),
    };
  })();
}
