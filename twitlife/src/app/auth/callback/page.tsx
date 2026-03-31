"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Auth callback — legacy route from Supabase OAuth.
 * Just redirects to the title screen in arcade mode.
 */
export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    router.push("/");
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-black">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-400 mb-4" />
        <p className="text-cyan-400 font-mono">REDIRECTING...</p>
      </div>
    </div>
  );
}
