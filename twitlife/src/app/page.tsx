"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  ChevronRight,
  RotateCcw,
  Dices,
  Loader2,
} from "lucide-react";
import { useGameState } from "@/hooks/useGameState";
import { useAudio } from "@/hooks/useAudio";

// Niche definitions
const NICHES = [
  {
    id: "tech",
    name: "Tech",
    description: "Disruptive. Contrarian.",
    icon: "💻",
  },
  {
    id: "local",
    name: "Local",
    description: "Community. Drama.",
    icon: "🏙️",
  },
  {
    id: "politics",
    name: "Politics",
    description: "Polarized. Ideological.",
    icon: "🏛️",
  },
  {
    id: "combat_sports",
    name: "Combat Sports",
    description: "Aggressive. Tribal.",
    icon: "🥊",
  },
];

function rollStat() {
  return Math.floor(Math.random() * 40) + 30; // 30-70
}

export default function TitleScreen() {
  const router = useRouter();
  const { character, legacy, loading, createCharacter } = useGameState();
  const { statDing } = useAudio();

  // UI State
  const [handle, setHandle] = useState("");
  const [selectedNiche, setSelectedNiche] = useState<string | null>(null);
  
  // Vector Avatar Creator State
  const [avatarStyle, setAvatarStyle] = useState<"personas" | "avataaars" | "open-peeps" | "pixel-art" | "bottts">("personas");
  const [avatarSeed, setAvatarSeed] = useState(() => Math.random().toString(36).substring(2, 9));
  const [avatarBg, setAvatarBg] = useState("b6e3f4");
  const [customAvatarUrl, setCustomAvatarUrl] = useState("");
  const [useCustomUrl, setUseCustomUrl] = useState(false);

  const generatedAvatarUrl = useCustomUrl && customAvatarUrl.trim()
    ? customAvatarUrl.trim()
    : `https://api.dicebear.com/9.x/${avatarStyle}/svg?seed=${encodeURIComponent(avatarSeed || handle || "twitlife")}&backgroundColor=${avatarBg}`;

  const handleRandomizeAvatar = () => {
    const styles: Array<"personas" | "avataaars" | "open-peeps" | "pixel-art" | "bottts"> = [
      "personas", "avataaars", "open-peeps", "pixel-art", "bottts"
    ];
    const bgs = ["b6e3f4", "c0aede", "d1d4f9", "ffd5dc", "ffdfbf", "1da1f2", "7952b3", "2ea44f", "000000"];
    
    setAvatarStyle(styles[Math.floor(Math.random() * styles.length)]);
    setAvatarSeed(Math.random().toString(36).substring(2, 10));
    setAvatarBg(bgs[Math.floor(Math.random() * bgs.length)]);
    setUseCustomUrl(false);
    statDing();
  };

  const [stats, setStats] = useState({
    aura: rollStat(),
    heat: rollStat(),
    insight: rollStat(),
  });
  const [rerollsRemaining, setRerollsRemaining] = useState(3);
  const [isCreating, setIsCreating] = useState(false);
  const [scene, setScene] = useState<"title" | "create">("title");

  // Redirect if character already exists
  useEffect(() => {
    if (!loading && character) {
      router.replace("/dashboard");
    }
  }, [character, loading, router]);

  const handleRollStats = () => {
    if (rerollsRemaining > 0) {
      setStats({
        aura: rollStat(),
        heat: rollStat(),
        insight: rollStat(),
      });
      setRerollsRemaining(rerollsRemaining - 1);
      statDing();
    }
  };

  const handleCreateCharacter = async () => {
    if (!handle || !selectedNiche) return;

    setIsCreating(true);
    try {
      // Create character with legacy bonuses if available and include custom avatar
      createCharacter(handle, selectedNiche, stats, generatedAvatarUrl);

      // Give a moment for the state to update, then navigate
      await new Promise((resolve) => setTimeout(resolve, 100));
      router.push("/dashboard");
    } catch (err) {
      console.error("Failed to create character:", err);
      setIsCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black crt-filter">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-400 mb-4" />
          <p className="text-cyan-400 font-mono text-lg">INITIALIZING...</p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // SCENE 1: Title Screen (INSERT COIN)
  // ============================================================================

  if (scene === "title") {
    return (
      <div className="min-h-screen bg-black crt-filter flex items-center justify-center px-4 py-8 relative overflow-hidden">
        {/* Scanlines effect */}
        <div className="absolute inset-0 pointer-events-none opacity-20">
          <div className="h-full bg-gradient-to-b from-transparent via-cyan-500 to-transparent animate-pulse" />
        </div>

        {/* Arcade grid background */}
        <div className="absolute inset-0 pointer-events-none opacity-10">
          <div
            className="w-full h-full"
            style={{
              backgroundImage: `linear-gradient(0deg, transparent 24%, rgba(0, 255, 255, 0.1) 25%, rgba(0, 255, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, 0.1) 75%, rgba(0, 255, 255, 0.1) 76%, transparent 77%, transparent),
                               linear-gradient(90deg, transparent 24%, rgba(0, 255, 255, 0.1) 25%, rgba(0, 255, 255, 0.1) 26%, transparent 27%, transparent 74%, rgba(0, 255, 255, 0.1) 75%, rgba(0, 255, 255, 0.1) 76%, transparent 77%, transparent)`,
              backgroundSize: "50px 50px",
            }}
          />
        </div>

        <div className="relative z-10 text-center space-y-8 w-full max-w-2xl">
          {/* Logo */}
          <div className="space-y-4 mb-12">
            <h1 className="text-7xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 animate-pulse font-mono drop-shadow-2xl">
              TWITLIFE
            </h1>

            <p className="text-cyan-400 font-mono text-lg tracking-widest animate-pulse opacity-75">
              ▮ ARCADE EDITION ▮
            </p>

            {/* INSERT COIN msg */}
            <div className="text-center mt-8 space-y-3">
              <p className="text-cyan-300 font-mono text-2xl">
                {legacy ? "CONTINUE LEGACY" : "INSERT COIN"}
              </p>

              {legacy && (
                <div className="text-sm text-amber-400 font-mono bg-amber-400/10 border border-amber-400/20 rounded-lg p-3 inline-block">
                  <div>Legacy from Gen {legacy.generation}: {legacy.handle}</div>
                  <div className="text-xs opacity-75 mt-1">
                    +{legacy.auraBonus} AURA • +{legacy.followerBonus} FOLLOWERS
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Main Button - "Press Start" */}
          <button
            onClick={() => setScene("create")}
            className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-black font-black py-4 px-8 rounded-lg text-xl tracking-wider animate-bounce transform transition-all hover:scale-105 active:scale-95 shadow-2xl font-mono"
          >
            ► PRESS START ◄
          </button>

          {/* Info text */}
          <div className="text-cyan-500 font-mono text-sm space-y-1 opacity-75">
            <p>Build your digital dynasty.</p>
            <p>Rise to power. Fall to the algorithms.</p>
            <p>Every generation brings new challenges.</p>
          </div>
        </div>
      </div>
    );
  }

  // ============================================================================
  // SCENE 2: Character Creation
  // ============================================================================

  return (
    <div className="min-h-screen bg-black crt-filter flex items-center justify-center px-4 py-8 relative overflow-hidden">
      {/* Scanlines */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <div className="h-full bg-gradient-to-b from-transparent via-cyan-500 to-transparent animate-pulse" />
      </div>

      <div className="relative z-10 w-full max-w-2xl space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h2 className="text-5xl font-black text-cyan-400 font-mono">NEW GAME</h2>
          <p className="text-cyan-300 font-mono">Define your legend</p>
        </div>

        {/* Card */}
        <div className="border-4 border-cyan-400 bg-black p-8 shadow-2xl space-y-6">
          {/* Handle Input */}
          <div>
            <label className="block text-cyan-300 font-mono mb-2 text-lg">
              ▶ HANDLE:
            </label>
            <div className="relative">
              <span className="absolute left-4 top-3 text-cyan-400 text-xl font-mono">@</span>
              <input
                type="text"
                value={handle}
                onChange={(e) => setHandle(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ""))}
                placeholder="your_handle"
                maxLength={20}
                className="w-full bg-cyan-400/10 border-2 border-cyan-400 pl-10 pr-4 py-3 text-cyan-300 placeholder-cyan-600 focus:outline-none focus:ring-2 focus:ring-cyan-400 font-mono text-lg"
              />
            </div>
          </div>

          {/* Niche Selection */}
          <div>
            <label className="block text-cyan-300 font-mono mb-3 text-lg">
              ▶ STARTING NICHE:
            </label>
            <div className="grid grid-cols-2 gap-3">
              {NICHES.map((niche) => (
                <button
                  key={niche.id}
                  onClick={() => setSelectedNiche(niche.id)}
                  className={`p-4 border-2 font-mono transition-all ${
                    selectedNiche === niche.id
                      ? "border-cyan-400 bg-cyan-400 text-black"
                      : "border-cyan-400 bg-black text-cyan-400 hover:bg-cyan-400/10"
                  }`}
                >
                  <div className="text-2xl mb-1">{niche.icon}</div>
                  <div className="font-bold text-sm">{niche.name}</div>
                  <div className="text-xs opacity-75">{niche.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Avatar Creator */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="block text-cyan-300 font-mono text-lg">
                ▶ CHARACTER PORTRAIT & STYLE:
              </label>
              <button
                type="button"
                onClick={handleRandomizeAvatar}
                className="text-xs font-mono border border-cyan-400 bg-cyan-400/20 text-cyan-300 hover:bg-cyan-400 hover:text-black px-3 py-1.5 rounded transition-all flex items-center gap-1.5"
              >
                <Dices className="w-3.5 h-3.5" /> RANDOMIZE AVATAR
              </button>
            </div>

            <div className="bg-cyan-400/5 border border-cyan-400 p-5 space-y-4 font-mono">
              <div className="flex flex-col md:flex-row gap-6 items-center md:items-start">
                {/* Live Avatar Frame */}
                <div className="relative group flex-shrink-0">
                  <div className="w-36 h-36 border-4 border-cyan-400 bg-black rounded-2xl overflow-hidden shadow-cyan-400/20 shadow-xl flex items-center justify-center relative">
                    <img
                      src={generatedAvatarUrl}
                      alt="Avatar Preview"
                      className="w-full h-full object-cover transition-all duration-300 transform group-hover:scale-105"
                      onError={(e) => {
                        // Fallback if custom URL fails to load
                        (e.target as HTMLImageElement).src = `https://api.dicebear.com/9.x/personas/svg?seed=${handle || "twitlife"}`;
                      }}
                    />
                  </div>
                  <div className="absolute -bottom-2 -right-2 bg-cyan-400 text-black text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">
                    {useCustomUrl ? "URL" : avatarStyle}
                  </div>
                </div>

                {/* Controls */}
                <div className="flex-1 w-full space-y-4 text-xs">
                  {/* Style Archetype Selector */}
                  <div>
                    <label className="block text-cyan-500 mb-1.5 font-bold uppercase tracking-wider text-[11px]">
                      ART STYLE ARCHETYPE
                    </label>
                    <div className="grid grid-cols-5 gap-1.5">
                      {[
                        { id: "personas", label: "Sleek", icon: "👤" },
                        { id: "avataaars", label: "BitLife", icon: "🧍" },
                        { id: "pixel-art", label: "Pixel", icon: "👾" },
                        { id: "open-peeps", label: "Peeps", icon: "🎨" },
                        { id: "bottts", label: "Bot", icon: "🤖" },
                      ].map((style) => (
                        <button
                          key={style.id}
                          type="button"
                          onClick={() => {
                            setAvatarStyle(style.id as any);
                            setUseCustomUrl(false);
                            statDing();
                          }}
                          className={`p-2 border text-center transition-all ${
                            !useCustomUrl && avatarStyle === style.id
                              ? "border-cyan-400 bg-cyan-400 text-black font-bold"
                              : "border-cyan-400/40 bg-black text-cyan-300 hover:border-cyan-400"
                          }`}
                        >
                          <div className="text-base">{style.icon}</div>
                          <div className="text-[10px] truncate">{style.label}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Seed / Feature Customizer */}
                  {!useCustomUrl && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-cyan-500 mb-1 font-bold text-[11px]">
                          DNA SEED (FACTION / LOOK)
                        </label>
                        <div className="relative">
                          <input
                            type="text"
                            value={avatarSeed}
                            onChange={(e) => setAvatarSeed(e.target.value)}
                            placeholder="Type any word..."
                            className="w-full bg-black border border-cyan-400/60 p-2 text-cyan-300 focus:outline-none focus:border-cyan-400 text-xs"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-cyan-500 mb-1 font-bold text-[11px]">
                          BACKGROUND AURA
                        </label>
                        <div className="flex gap-1.5 items-center flex-wrap pt-0.5">
                          {[
                            { hex: "b6e3f4", label: "Sky" },
                            { hex: "c0aede", label: "Purple" },
                            { hex: "ffd5dc", label: "Pink" },
                            { hex: "1da1f2", label: "Twitter" },
                            { hex: "7952b3", label: "Royal" },
                            { hex: "2ea44f", label: "Emerald" },
                            { hex: "000000", label: "Dark" },
                          ].map((bg) => (
                            <button
                              key={bg.hex}
                              type="button"
                              onClick={() => setAvatarBg(bg.hex)}
                              className={`w-6 h-6 rounded-full border-2 transition-transform ${
                                avatarBg === bg.hex ? "border-white scale-110 shadow" : "border-transparent hover:scale-105"
                              }`}
                              style={{ backgroundColor: `#${bg.hex}` }}
                              title={bg.label}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Custom URL Input Toggle */}
                  <div className="pt-1 border-t border-cyan-400/20">
                    <button
                      type="button"
                      onClick={() => setUseCustomUrl(!useCustomUrl)}
                      className="text-[11px] text-cyan-400 underline hover:text-cyan-300 flex items-center gap-1"
                    >
                      {useCustomUrl ? "◄ Return to Vector Creator" : "► Paste Custom Image URL / PFP Link"}
                    </button>
                    {useCustomUrl && (
                      <input
                        type="url"
                        value={customAvatarUrl}
                        onChange={(e) => setCustomAvatarUrl(e.target.value)}
                        placeholder="https://example.com/my-avatar.png"
                        className="w-full mt-2 bg-black border border-cyan-400 p-2 text-cyan-300 text-xs focus:outline-none"
                      />
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stat Roll */}
          <div>
            <label className="block text-cyan-300 font-mono mb-3 text-lg">
              ▶ STARTING STATS: ({rerollsRemaining} rolls left)
            </label>
            <div className="space-y-3">
              {/* AURA */}
              <div className="border border-cyan-400 p-3 bg-cyan-400/5">
                <div className="flex justify-between mb-2 font-mono text-cyan-300">
                  <span>AURA</span>
                  <span className="text-cyan-400 font-bold text-lg">{stats.aura}</span>
                </div>
                <div className="w-full bg-cyan-400/20 h-3 border border-cyan-400">
                  <div
                    className="bg-gradient-to-r from-cyan-400 to-cyan-600 h-full transition-all"
                    style={{ width: `${stats.aura}%` }}
                  />
                </div>
              </div>

              {/* HEAT */}
              <div className="border border-red-400 p-3 bg-red-400/5">
                <div className="flex justify-between mb-2 font-mono text-red-300">
                  <span>HEAT</span>
                  <span className="text-red-400 font-bold text-lg">{stats.heat}</span>
                </div>
                <div className="w-full bg-red-400/20 h-3 border border-red-400">
                  <div
                    className="bg-gradient-to-r from-red-400 to-red-600 h-full transition-all"
                    style={{ width: `${stats.heat}%` }}
                  />
                </div>
              </div>

              {/* INSIGHT */}
              <div className="border border-purple-400 p-3 bg-purple-400/5">
                <div className="flex justify-between mb-2 font-mono text-purple-300">
                  <span>INSIGHT</span>
                  <span className="text-purple-400 font-bold text-lg">{stats.insight}</span>
                </div>
                <div className="w-full bg-purple-400/20 h-3 border border-purple-400">
                  <div
                    className="bg-gradient-to-r from-purple-400 to-purple-600 h-full transition-all"
                    style={{ width: `${stats.insight}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Reroll Button */}
            <button
              onClick={handleRollStats}
              disabled={rerollsRemaining === 0}
              className="w-full mt-4 border-2 border-cyan-400 bg-cyan-400 text-black hover:bg-cyan-300 disabled:border-gray-500 disabled:bg-gray-600 disabled:text-gray-400 font-mono font-bold py-2 rounded transition-all flex items-center justify-center gap-2"
            >
              <Dices className="w-4 h-4" /> REROLL ({rerollsRemaining})
            </button>
          </div>

          {/* Ready Check */}
          {handle && selectedNiche && (
            <div className="border-2 border-green-400 bg-green-400/10 p-3 text-center font-mono text-green-400">
              ✓ READY TO ENTER THE GRID
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={() => setScene("title")}
              className="flex-1 border-2 border-cyan-400 bg-black text-cyan-400 hover:bg-cyan-400/10 font-mono font-bold py-3 transition-all"
            >
              ◄ BACK
            </button>
            <button
              onClick={handleCreateCharacter}
              disabled={!handle || !selectedNiche || isCreating}
              className="flex-1 border-2 border-cyan-400 bg-cyan-400 text-black hover:bg-cyan-300 disabled:border-gray-500 disabled:bg-gray-600 disabled:text-gray-400 font-mono font-bold py-3 transition-all flex items-center justify-center gap-2"
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> LOADING
                </>
              ) : (
                <>
                  ENTER GRID <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .crt-filter {
          filter: contrast(1.1) brightness(0.95);
          background-color: rgb(0, 0, 0);
        }

        @keyframes scanlines {
          0% {
            transform: translateY(0);
          }
          100% {
            transform: translateY(10px);
          }
        }

        @keyframes glitch {
          0% {
            text-shadow: 2px 0 #00ffff, -2px 0 #ff00ff;
          }
          50% {
            text-shadow: -2px 0 #00ffff, 2px 0 #ff00ff;
          }
          100% {
            text-shadow: 2px 0 #00ffff, -2px 0 #ff00ff;
          }
        }
      `}</style>
    </div>
  );
}
