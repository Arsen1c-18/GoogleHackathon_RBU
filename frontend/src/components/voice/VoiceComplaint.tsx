"use client";

import { useRef, useState } from "react";
import { useAuth } from "@/components/providers/AuthProvider";
import { apiPost } from "@/lib/api";
import {
  VOICE_LANGS,
  normalizeVoiceLang,
  recordMic,
  speak,
  transcribeAudio,
  type VoiceLang,
} from "@/lib/voice";

type Stage = "pick" | "recording" | "review" | "done";

export default function VoiceComplaint() {
  const { getIdToken, user } = useAuth();
  const [lang, setLang] = useState<VoiceLang>("en");
  const [stage, setStage] = useState<Stage>("pick");
  const [level, setLevel] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [provider, setProvider] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [complaintId, setComplaintId] = useState("");
  const stopRef = useRef<(() => Promise<Blob>) | null>(null);

  const start = async () => {
    setError(null);
    try {
      const { stop } = await recordMic(setLevel);
      stopRef.current = stop;
      setStage("recording");
    } catch {
      setError(
        lang === "hi"
          ? "माइक की अनुमति दें और फिर कोशिश करें"
          : "Allow mic access and try again"
      );
    }
  };

  const stopAndTranscribe = async () => {
    if (!stopRef.current) return;
    setStage("review");
    setError(null);
    try {
      const blob = await stopRef.current();
      stopRef.current = null;
      setLevel(0);
      const result = await transcribeAudio(blob, lang, getIdToken);
      setTranscript(result.text);
      setProvider(result.provider);
      speak(result.text, lang);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Transcription failed");
      setStage("pick");
    }
  };

  const submit = async () => {
    if (!transcript.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      // Optional structuring via Gemini (falls back to heuristic on backend)
      let structured: Record<string, string> = {};
      try {
        const s = await apiPost<{ structured: Record<string, string> }>(
          "/api/voice/structure",
          { transcript, language: lang }
        );
        structured = s.structured ?? {};
      } catch {
        structured = {};
      }
      const created = await apiPost<{ id: string }>("/api/complaints", {
        transcript_raw: transcript,
        language: lang,
        title: structured.title,
        category: structured.category,
        location: structured.location,
        description_en: structured.description_en,
      });
      setComplaintId(created.id);
      setStage("done");
      speak(
        lang === "hi"
          ? "शिकायत सफलतापूर्वक दर्ज हो गई"
          : "Complaint filed successfully",
        lang
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Submit failed — sign in first");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-md rounded-xl border p-6 space-y-4">
      <div className="flex gap-2">
        {VOICE_LANGS.map((l) => (
          <button
            key={l.code}
            onClick={() => setLang(normalizeVoiceLang(l.code))}
            className={`flex-1 rounded-full border px-4 py-2 ${
              lang === l.code ? "bg-black text-white dark:bg-white dark:text-black" : ""
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>

      {!user && (
        <p className="text-sm text-amber-600">
          {lang === "hi"
            ? "शिकायत दर्ज करने के लिए पहले लॉगिन करें"
            : "Sign in first to file a complaint"}
        </p>
      )}

      {stage === "pick" && (
        <button
          onClick={start}
          className="w-full rounded-full bg-black px-5 py-4 text-lg text-white dark:bg-white dark:text-black"
        >
          {lang === "hi" ? "🎙️ बोलना शुरू करें" : "🎙️ Tap to speak"}
        </button>
      )}

      {stage === "recording" && (
        <div className="space-y-3 text-center">
          <div className="h-2 rounded bg-zinc-200 dark:bg-zinc-800">
            <div
              className="h-2 rounded bg-green-500 transition-all"
              style={{ width: `${Math.min(100, level * 300)}%` }}
            />
          </div>
          <p className="text-sm">
            {lang === "hi" ? "सुन रहे हैं…" : "Listening…"}
          </p>
          <button
            onClick={stopAndTranscribe}
            className="w-full rounded-full border px-5 py-3"
          >
            {lang === "hi" ? "रोकें और भेजें" : "Stop and transcribe"}
          </button>
        </div>
      )}

      {stage === "review" && (
        <div className="space-y-3">
          <p className="text-sm text-zinc-500">
            {lang === "hi" ? "आपने कहा:" : "You said:"} ({provider})
          </p>
          <p className="rounded border p-3 min-h-20">
            {transcript || (lang === "hi" ? "पहचान रहे हैं…" : "Transcribing…")}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => speak(transcript, lang)}
              className="flex-1 rounded-full border px-4 py-2"
            >
              {lang === "hi" ? "🔊 फिर सुनें" : "🔊 Replay"}
            </button>
            <button
              onClick={submit}
              disabled={submitting || !transcript.trim() || !user}
              className="flex-1 rounded-full bg-black px-4 py-2 text-white disabled:opacity-40 dark:bg-white dark:text-black"
            >
              {submitting
                ? "…"
                : lang === "hi"
                  ? "जमा करें"
                  : "Submit"}
            </button>
          </div>
          <button onClick={() => setStage("pick")} className="text-sm underline">
            {lang === "hi" ? "फिर से बोलें" : "Record again"}
          </button>
        </div>
      )}

      {stage === "done" && (
        <div className="space-y-3 text-center">
          <p className="text-lg font-semibold">
            {lang === "hi" ? "✅ दर्ज हो गई" : "✅ Filed"} #{complaintId.slice(0, 8)}
          </p>
          <button
            onClick={() => {
              setStage("pick");
              setTranscript("");
              setComplaintId("");
            }}
            className="rounded-full border px-5 py-2"
          >
            {lang === "hi" ? "नई शिकायत" : "New complaint"}
          </button>
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
