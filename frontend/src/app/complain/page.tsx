import VoiceComplaint from "@/components/voice/VoiceComplaint";

export const metadata = {
  title: "File complaint by voice",
  description: "Zero-typing voice complaint lodging in English and Hindi",
};

export default function ComplainPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 gap-6">
      <h1 className="text-2xl font-semibold">Voice complaint / वॉइस शिकायत</h1>
      <p className="text-sm text-zinc-500">
        No typing needed — speak in English or Hindi. / टाइपिंग की ज़रूरत नहीं।
      </p>
      <VoiceComplaint />
    </main>
  );
}
