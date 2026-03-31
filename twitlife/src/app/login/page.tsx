"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

/**
 * Login page — in arcade mode, we skip auth and go straight to character creation.
 * If user already has a character, redirect to dashboard.
 */
export default function LoginPage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (loading) return;
    if (user) {
      // Already has a character, go to dashboard
      router.push("/dashboard");
    } else {
      // No character — go to title screen to create one
      router.push("/");
    }
  }, [user, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-black">
      <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
    </div>
  );
}
