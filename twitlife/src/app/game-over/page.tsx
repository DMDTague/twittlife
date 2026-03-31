"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Crown, TrendingUp, DollarSign, AlertCircle, RotateCcw, Trophy } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

interface FinalStats {
  character: {
    handle: string;
    niche: string;
    generation: number;
    account_tier: string;
    deplatform_reason: string;
  };
  stats: {
    aura_peak: number;
    followers_peak: number;
    wealth_accumulated: number;
    posts_made: number;
    engagement_total: number;
    days_active: number;
  };
  legacy: {
    aura_bonus: number;
    wealth_bonus: number;
    follower_bonus: number;
  };
}

function GameOverContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { legacy, signOut } = useAuth();

  const [stats, setStats] = useState<FinalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);

  useEffect(() => {
    // Build stats from legacy data if available
    if (legacy) {
      setStats({
        character: {
          handle: legacy.handle,
          niche: "general",
          generation: legacy.generation,
          account_tier: legacy.tierReached,
          deplatform_reason: searchParams.get("reason") || legacy.cause || "Unknown",
        },
        stats: {
          aura_peak: legacy.auraBonus * 10,
          followers_peak: legacy.followerBonus * 10,
          wealth_accumulated: legacy.wealthBonus * 10,
          posts_made: 0,
          engagement_total: 0,
          days_active: 0,
        },
        legacy: {
          aura_bonus: legacy.auraBonus,
          wealth_bonus: legacy.wealthBonus,
          follower_bonus: legacy.followerBonus,
        },
      });
    } else {
      // No legacy data — create placeholder
      setStats({
        character: {
          handle: "unknown",
          niche: "general",
          generation: 1,
          account_tier: "guest",
          deplatform_reason: searchParams.get("reason") || "Unknown",
        },
        stats: {
          aura_peak: 1500,
          followers_peak: 500,
          wealth_accumulated: 0,
          posts_made: 0,
          engagement_total: 0,
          days_active: 0,
        },
        legacy: { aura_bonus: 0, wealth_bonus: 0, follower_bonus: 0 },
      });
    }
    setLoading(false);
  }, [legacy, searchParams]);

  const handleStartNextGeneration = async () => {
    setIsStarting(true);
    router.push("/");
  };

  const handleSignOut = () => {
    signOut();
    router.push("/");
  };

  if (loading || !stats) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4" />
          <p className="text-white text-lg">Loading your final stats...</p>
        </div>
      </div>
    );
  }

  const reasonColors: { [key: string]: string } = {
    toxicity_fatigue: "text-red-400",
    crucible_failures: "text-orange-400",
    mass_report: "text-pink-400",
    default: "text-yellow-400",
  };

  const reasonColor = reasonColors[stats.character.deplatform_reason] || reasonColors.default;

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-red-950 to-black overflow-hidden">
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 right-0 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-8 space-y-4">
            <div className="text-6xl mb-4">💀</div>
            <h1 className="text-4xl md:text-5xl font-black text-white mb-2">ACCOUNT TERMINATED</h1>
            <p className="text-xl text-gray-300">Your run has ended.</p>
            <p className={`text-lg font-bold ${reasonColor}`}>
              Cause: {stats.character.deplatform_reason.replace(/_/g, " ").toUpperCase()}
            </p>
          </div>

          <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl space-y-8">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <Trophy className="w-6 h-6 text-yellow-400" />
                FINAL STATS
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">HIGHEST TIER</p>
                  <p className="text-2xl font-bold text-purple-400 flex items-center gap-2">
                    <Crown className="w-5 h-5" />
                    {stats.character.account_tier.toUpperCase()}
                  </p>
                </div>

                <div className="p-4 bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">FOLLOWERS PEAK</p>
                  <p className="text-2xl font-bold text-blue-400 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    {stats.stats.followers_peak.toLocaleString()}
                  </p>
                </div>

                <div className="p-4 bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">WEALTH ACCUMULATED</p>
                  <p className="text-2xl font-bold text-green-400 flex items-center gap-2">
                    <DollarSign className="w-5 h-5" />
                    {stats.stats.wealth_accumulated.toLocaleString()}₵
                  </p>
                </div>

                <div className="p-4 bg-gradient-to-br from-orange-500/10 to-orange-500/5 border border-orange-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">GENERATION</p>
                  <p className="text-2xl font-bold text-orange-400">
                    Gen {stats.character.generation}
                  </p>
                </div>
              </div>
            </div>

            {/* Legacy Bonuses */}
            {(stats.legacy.aura_bonus > 0 || stats.legacy.wealth_bonus > 0 || stats.legacy.follower_bonus > 0) && (
              <div className="space-y-4 p-4 bg-gradient-to-r from-yellow-500/10 to-amber-500/10 border border-yellow-500/20 rounded-lg">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="text-2xl">✨</span>
                  LEGACY BONUSES FOR GEN {stats.character.generation + 1}
                </h3>
                <p className="text-gray-300 text-sm">
                  Your achievements carry forward. Your next generation starts stronger.
                </p>
                <div className="grid grid-cols-3 gap-4 mt-4">
                  <div className="text-center">
                    <p className="text-gray-400 text-xs mb-1">AURA</p>
                    <p className="text-xl font-bold text-blue-400">+{stats.legacy.aura_bonus}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-400 text-xs mb-1">WEALTH</p>
                    <p className="text-xl font-bold text-green-400">+{stats.legacy.wealth_bonus.toLocaleString()}₵</p>
                  </div>
                  <div className="text-center">
                    <p className="text-gray-400 text-xs mb-1">FOLLOWERS</p>
                    <p className="text-xl font-bold text-purple-400">+{stats.legacy.follower_bonus.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-3">
              <button
                onClick={handleStartNextGeneration}
                disabled={isStarting}
                className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2 text-lg"
              >
                {isStarting ? (
                  <>
                    <span className="inline-block animate-spin">⌛</span> Starting...
                  </>
                ) : (
                  <>
                    <RotateCcw className="w-5 h-5" />
                    START NEXT GENERATION
                  </>
                )}
              </button>

              <button
                onClick={handleSignOut}
                className="w-full bg-white/10 hover:bg-white/20 text-white font-bold py-2 rounded-lg transition-all"
              >
                Wipe Everything & Start Fresh
              </button>
            </div>

            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
              <p className="text-blue-300 text-sm">
                Legacy bonuses from this run will apply to your next character.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function GameOverPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4" />
          <p className="text-white text-lg">Loading your final stats...</p>
        </div>
      </div>
    }>
      <GameOverContent />
    </Suspense>
  );
}
