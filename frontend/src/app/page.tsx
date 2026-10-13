"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/components/providers/AuthProvider";
import { apiGet } from "@/lib/api";

export default function Home() {
  const { user, loading, logout } = useAuth();
  const [backendStatus, setBackendStatus] = useState<string>("checking...");

  useEffect(() => {
    apiGet<{ status: string }>("/health")
      .then((d) => setBackendStatus(d.status))
      .catch(() => setBackendStatus("unreachable (is FastAPI running?)"));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 gap-6">
      <h1 className="text-3xl font-semibold">Next.js + FastAPI + Firebase</h1>
      <div className="rounded-xl border p-4 w-full max-w-md space-y-2 text-sm">
        <p>
          <strong>Frontend:</strong> OK
        </p>
        <p>
          <strong>Backend:</strong> {backendStatus}
        </p>
        <p>
          <strong>Firebase user:</strong>{" "}
          {loading ? "loading..." : user ? user.email : "not signed in"}
        </p>
      </div>
      <div className="flex gap-3 flex-wrap justify-center">
        <Link
          href="/complain"
          className="rounded-full bg-green-700 px-5 py-2 text-white"
        >
          🎙️ File voice complaint
        </Link>
        {!user ? (
          <Link
            href="/login"
            className="rounded-full bg-black px-5 py-2 text-white dark:bg-white dark:text-black"
          >
            Go to Login
          </Link>
        ) : (
          <button
            onClick={logout}
            className="rounded-full border px-5 py-2"
          >
            Logout
          </button>
        )}
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          className="rounded-full border px-5 py-2"
        >
          API Docs
        </a>
      </div>
    </main>
  );
}
