"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Sparkles, ChevronRight, ChevronLeft, Loader2, Dices } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

// Niche definitions
const NICHES = [
  {
    id: "tech",
    name: "Tech",
    description: "Contrarian, intellectual, startup-focused",
    icon: "💻",
    bonus: "+20 INSIGHT",
  },
  {
    id: "politics",
    name: "Politics",
    description: "Ideological, polarized, current-events",
    icon: "🏛️",
    bonus: "+20 HEAT",
  },
  {
    id: "combat_sports",
    name: "Combat Sports",
    description: "Aggressive, tribalistic, fitness-focused",
    icon: "🥊",
    bonus: "+20 HEAT",
  },
  {
    id: "gaming",
    name: "Gaming",
    description: "Casual, community-focused, entertainment",
    icon: "🎮",
    bonus: "+20 AURA",
  },
  {
    id: "general",
    name: "General",
    description: "Balanced, no niche bonus",
    icon: "📱",
    bonus: "No bonus",
  },
];

function rollStat() {
  return Math.floor(Math.random() * 40) + 30; // 30-70 range for balance
}

export default function CreateAccountPage() {
  const router = useRouter();
  const { user, character, createCharacter } = useAuth();

  const [step, setStep] = useState<"handle" | "niche" | "stats" | "review">("handle");
  const [handle, setHandle] = useState("");
  const [handleError, setHandleError] = useState("");
  const [handleAvailable, setHandleAvailable] = useState<boolean | null>(null);
  const [selectedNiche, setSelectedNiche] = useState<string | null>(null);
  const [stats, setStats] = useState({
    aura: rollStat(),
    heat: rollStat(),
    insight: rollStat(),
  });
  const [rerollsRemaining, setRerollsRemaining] = useState(3);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [checkingHandle, setCheckingHandle] = useState(false);

  // If character already exists, redirect to dashboard
  useEffect(() => {
    if (character) {
      router.push("/dashboard");
    }
  }, [character, router]);

  // If not authenticated, redirect to login
  useEffect(() => {
    if (!user) {
      router.push("/login");
    }
  }, [user, router]);

  // ============================================================================
  // Handle Validation
  // ============================================================================

  const checkHandleAvailability = async (h: string) => {
    if (h.length < 3) {
      setHandleAvailable(null);
      setHandleError("Handle must be at least 3 characters");
      return;
    }

    if (h.length > 25) {
      setHandleAvailable(null);
      setHandleError("Handle must be 25 characters or less");
      return;
    }

    if (!h.match(/^[a-zA-Z0-9_]+$/)) {
      setHandleAvailable(null);
      setHandleError("Handle can only contain letters, numbers, and underscores");
      return;
    }

    setCheckingHandle(true);
    try {
      const response = await fetch("/api/auth/check-handle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ handle: h }),
      });

      const data = await response.json();
      setHandleAvailable(data.available);
      setHandleError(data.available ? "" : "This handle is already taken");
    } catch (err) {
      setHandleAvailable(false);
      setHandleError("Failed to check handle availability");
    } finally {
      setCheckingHandle(false);
    }
  };

  const handleHandleChange = (value: string) => {
    const sanitized = value.toLowerCase().replace(/[^a-z0-9_]/g, "");
    setHandle(sanitized);
    checkHandleAvailability(sanitized);
  };

  // ============================================================================
  // Roll Stats
  // ============================================================================

  const rollNewStats = () => {
    if (rerollsRemaining > 0) {
      setStats({
        aura: rollStat(),
        heat: rollStat(),
        insight: rollStat(),
      });
      setRerollsRemaining(rerollsRemaining - 1);
    }
  };

  // ============================================================================
  // Create Character
  // ============================================================================

  const handleCreateCharacter = async () => {
    if (!handle || !selectedNiche || !handleAvailable) {
      setError("Missing required fields");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await createCharacter(handle, selectedNiche, stats);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Failed to create character");
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // Render Steps
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-blue-950 to-black flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Create Your Legend</h1>
          <p className="text-gray-400">
            Step {step === "handle" ? "1" : step === "niche" ? "2" : step === "stats" ? "3" : "4"} of 4
          </p>
        </div>

        {/* Card */}
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl">
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* STEP 1: Handle Selection */}
          {step === "handle" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Choose Your Handle</h2>
                <p className="text-gray-400">
                  This will be your public @username. You can't change it later.
                </p>
              </div>

              <div>
                <label className="block text-white text-sm font-medium mb-3">
                  Your Handle
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-3 text-gray-500 text-lg">@</span>
                  <input
                    type="text"
                    value={handle}
                    onChange={(e) => handleHandleChange(e.target.value)}
                    placeholder="yourhandle"
                    maxLength={25}
                    className="w-full bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Status */}
                <div className="mt-3 min-h-6">
                  {checkingHandle && (
                    <p className="text-blue-400 text-sm flex items-center gap-2">
                      <Loader2 className="w-3 h-3 animate-spin" /> Checking...
                    </p>
                  )}
                  {!checkingHandle && handleAvailable === true && (
                    <p className="text-green-400 text-sm">✓ Handle available</p>
                  )}
                  {!checkingHandle && handleAvailable === false && (
                    <p className="text-red-400 text-sm">{handleError}</p>
                  )}
                </div>

                <p className="text-gray-500 text-xs mt-2">
                  3-25 characters, letters/numbers/underscores only
                </p>
              </div>

              <button
                onClick={() => setStep("niche")}
                disabled={!handleAvailable || isLoading}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
              >
                Continue <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* STEP 2: Niche Selection */}
          {step === "niche" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Pick Your Niche</h2>
                <p className="text-gray-400">
                  Your niche gives you starting bonuses and affects your content style.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {NICHES.map((niche) => (
                  <button
                    key={niche.id}
                    onClick={() => setSelectedNiche(niche.id)}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      selectedNiche === niche.id
                        ? "border-blue-500 bg-blue-500/10"
                        : "border-white/10 bg-white/5 hover:border-white/20"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{niche.icon}</span>
                      <div>
                        <h3 className="text-white font-bold">{niche.name}</h3>
                        <p className="text-gray-400 text-xs">{niche.description}</p>
                        <p className="text-blue-400 text-xs font-semibold mt-1">{niche.bonus}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep("handle")}
                  className="flex-1 bg-white/10 hover:bg-white/20 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  <ChevronLeft className="w-4 h-4" /> Back
                </button>
                <button
                  onClick={() => setStep("stats")}
                  disabled={!selectedNiche || isLoading}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  Continue <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Stat Roll */}
          {step === "stats" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Roll Your Stats</h2>
                <p className="text-gray-400">
                  Higher stats mean better starting abilities. You can re-roll {rerollsRemaining} more{" "}
                  {rerollsRemaining === 1 ? "time" : "times"}.
                </p>
              </div>

              {/* Stat Display */}
              <div className="space-y-3">
                <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-white font-bold">AURA (Charisma)</span>
                    <span className="text-2xl font-bold text-blue-400">{stats.aura}</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full"
                      style={{ width: `${stats.aura}%` }}
                    />
                  </div>
                </div>

                <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-white font-bold">HEAT (Toxicity)</span>
                    <span className="text-2xl font-bold text-red-400">{stats.heat}</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-red-400 to-red-600 h-2 rounded-full"
                      style={{ width: `${stats.heat}%` }}
                    />
                  </div>
                </div>

                <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-white font-bold">INSIGHT (IQ)</span>
                    <span className="text-2xl font-bold text-purple-400">{stats.insight}</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-400 to-purple-600 h-2 rounded-full"
                      style={{ width: `${stats.insight}%` }}
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={rollNewStats}
                disabled={rerollsRemaining === 0}
                className="w-full bg-white/10 hover:bg-white/20 disabled:bg-gray-700 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
              >
                <Dices className="w-4 h-4" /> Roll Again ({rerollsRemaining})
              </button>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep("niche")}
                  className="flex-1 bg-white/10 hover:bg-white/20 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  <ChevronLeft className="w-4 h-4" /> Back
                </button>
                <button
                  onClick={() => setStep("review")}
                  disabled={isLoading}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  Review <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: Review & Confirm */}
          {step === "review" && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Confirm Your Character</h2>
                <p className="text-gray-400">
                  Ready to start your legend?
                </p>
              </div>

              {/* Character Summary */}
              <div className="space-y-3">
                <div className="p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-400/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">HANDLE</p>
                  <p className="text-white text-xl font-bold">@{handle}</p>
                </div>

                <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">NICHE</p>
                  <p className="text-white text-lg font-bold">
                    {NICHES.find((n) => n.id === selectedNiche)?.name}
                  </p>
                </div>

                <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-3">STARTING STATS</p>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-300">AURA:</span>
                      <span className="text-blue-400 font-bold">{stats.aura}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">HEAT:</span>
                      <span className="text-red-400 font-bold">{stats.heat}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">INSIGHT:</span>
                      <span className="text-purple-400 font-bold">{stats.insight}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                <p className="text-green-400 text-sm">
                  <Sparkles className="w-4 h-4 inline mr-2" />
                  You'll start with 1,500 AURA, 500 followers, and 0 ₵ wealth.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep("stats")}
                  className="flex-1 bg-white/10 hover:bg-white/20 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  <ChevronLeft className="w-4 h-4" /> Back
                </button>
                <button
                  onClick={handleCreateCharacter}
                  disabled={isLoading}
                  className="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                  {isLoading ? "Creating..." : "Start Your Run"}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <Link href="/login" className="text-gray-400 hover:text-gray-300 text-sm">
            Or{" "}
            <button
              onClick={() => {
                // They can sign out or switch accounts here if needed
              }}
              className="text-blue-400 hover:text-blue-300"
            >
              use a different account
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}
