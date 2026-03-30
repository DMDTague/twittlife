"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Crown, TrendingUp, DollarSign, AlertCircle, RotateCcw, History, Trophy } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

interface FinalStats {
  character: {
    handle: string;
    niche: string;
    generation: number;
    account_tier: string;
    deplatform_reason: string;
    deplatform_at: string;
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
    tier_bonus_multiplier: number;
  };
}

export default function GameOverPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, character, signOut } = useAuth();

  const [stats, setStats] = useState<FinalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);

  // Load final stats from API
  useEffect(() => {
    if (!user || !character) {
      router.push("/login");
      return;
    }

    const fetchStats = async () => {
      try {
        // For now, we'll show placeholder stats
        // In Phase 2, this will fetch from the API
        setStats({
          character: {
            handle: character.name,
            niche: character.niche,
            generation: character.generation,
            account_tier: character.account_tier,
            deplatform_reason: searchParams.get("reason") || "Unknown",
            deplatform_at: new Date().toISOString(),
          },
          stats: {
            aura_peak: 8750,
            followers_peak: 125000,
            wealth_accumulated: 45320,
            posts_made: 348,
            engagement_total: 1245000,
            days_active: 47.5,
          },
          legacy: {
            aura_bonus: 150,
            wealth_bonus: 21660,
            follower_bonus: 1000,
            tier_bonus_multiplier: 1.1,
          },
        });
      } catch (err) {
        console.error("Failed to load stats:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user, character, router, searchParams]);

  const handleStartNextGeneration = async () => {
    setIsStarting(true);
    try {
      // TODO: Call /api/game/new-generation
      // Then redirect to /create-account
      router.push("/create-account");
    } catch (err) {
      console.error("Failed to start next generation:", err);
      setIsStarting(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
      router.push("/login");
    } catch (err) {
      console.error("Failed to sign out:", err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4" />
          <p className="text-white text-lg">Loading your final stats...</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <p className="text-white">Failed to load game over screen</p>
      </div>
    );
  }

  // Determine deplatform reason color
  const reasonColors: { [key: string]: string } = {
    toxicity_fatigue: "text-red-400",
    crucible_failures: "text-orange-400",
    mass_report: "text-pink-400",
    default: "text-yellow-400",
  };

  const reasonColor = reasonColors[stats.character.deplatform_reason] || reasonColors.default;

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-red-950 to-black overflow-hidden">
      {/* Animated background effect */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-0 right-0 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-2xl">
          {/* Game Over Header */}
          <div className="text-center mb-8 space-y-4">
            <div className="text-6xl mb-4">💀</div>
            <h1 className="text-4xl md:text-5xl font-black text-white mb-2">ACCOUNT TERMINATED</h1>
            <p className="text-xl text-gray-300">Your run has ended.</p>
            <p className={`text-lg font-bold ${reasonColor}`}>
              Cause: {stats.character.deplatform_reason.replace(/_/g, " ").toUpperCase()}
            </p>
          </div>

          {/* Main Card */}
          <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl space-y-8">
            {/* Final Stats Section */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <Trophy className="w-6 h-6 text-yellow-400" />
                FINAL STATS
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Tier */}
                <div className="p-4 bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">HIGHEST TIER</p>
                  <p className="text-2xl font-bold text-purple-400 flex items-center gap-2">
                    <Crown className="w-5 h-5" />
                    {stats.character.account_tier.toUpperCase()}
                  </p>
                </div>

                {/* Followers */}
                <div className="p-4 bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">FOLLOWERS PEAK</p>
                  <p className="text-2xl font-bold text-blue-400 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    {stats.stats.followers_peak.toLocaleString()}
                  </p>
                </div>

                {/* Wealth */}
                <div className="p-4 bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">WEALTH ACCUMULATED</p>
                  <p className="text-2xl font-bold text-green-400 flex items-center gap-2">
                    <DollarSign className="w-5 h-5" />
                    {stats.stats.wealth_accumulated.toLocaleString()}₵
                  </p>
                </div>

                {/* Days */}
                <div className="p-4 bg-gradient-to-br from-orange-500/10 to-orange-500/5 border border-orange-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">DAYS ACTIVE</p>
                  <p className="text-2xl font-bold text-orange-400">
                    {stats.stats.days_active.toFixed(1)}d
                  </p>
                </div>

                {/* Posts */}
                <div className="p-4 bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border border-cyan-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">POSTS MADE</p>
                  <p className="text-2xl font-bold text-cyan-400">
                    {stats.stats.posts_made.toLocaleString()}
                  </p>
                </div>

                {/* Engagement */}
                <div className="p-4 bg-gradient-to-br from-pink-500/10 to-pink-500/5 border border-pink-500/20 rounded-lg">
                  <p className="text-gray-400 text-xs font-medium mb-1">TOTAL ENGAGEMENT</p>
                  <p className="text-2xl font-bold text-pink-400">
                    {(stats.stats.engagement_total / 1000000).toFixed(1)}M
                  </p>
                </div>
              </div>
            </div>

            {/* Legacy Bonuses */}
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

            {/* Action Buttons */}
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

              <div className="grid grid-cols-2 gap-3">
                <Link href="/leaderboard">
                  <button className="w-full bg-white/10 hover:bg-white/20 text-white font-bold py-2 rounded-lg transition-all flex items-center justify-center gap-2">
                    <Trophy className="w-4 h-4" />
                    Leaderboard
                  </button>
                </Link>

                <button
                  onClick={handleSignOut}
                  className="w-full bg-white/10 hover:bg-white/20 text-white font-bold py-2 rounded-lg transition-all"
                >
                  Logout
                </button>
              </div>
            </div>

            {/* Info Footer */}
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
              <p className="text-blue-300 text-sm">
                Your character data is saved forever. View your{" "}
                <Link href="/account-history" className="underline hover:no-underline">
                  account history
                </Link>{" "}
                to see all past generations.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
