"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

/**
 * Create Account page — in arcade mode, redirect to the title screen
 * which has character creation built in.
 */
export default function CreateAccountPage() {
  const router = useRouter();
  const { character, loading } = useAuth();

  useEffect(() => {
    if (loading) return;
    if (character) {
      // Already has a character, go to dashboard
      router.push("/dashboard");
    } else {
      // No character — go to title screen (which has character creation)
      router.push("/");
    }
  }, [character, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-black">
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400 mx-auto mb-4" />
        <p className="text-cyan-400 font-mono">REDIRECTING...</p>
      </div>
    </div>
  );
}
