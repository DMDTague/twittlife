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
  
  // Avatar Builder State
  const [gender, setGender] = useState("male");
  const [hairColor, setHairColor] = useState("black");
  const [eyeColor, setEyeColor] = useState("brown");
  const [hairstyle, setHairstyle] = useState("short");
  const [skinTone, setSkinTone] = useState("light");

  const generatedAvatarUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(
    `A vibrant 2D cartoon avatar portrait of a ${gender} with ${skinTone} skin, ${hairColor} ${hairstyle} hair and ${eyeColor} eyes, flat vector art style, clean lines, vibrant colors, solid white background`
  )}?width=256&height=256&nologo=true`;

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
      router.push("/dashboard");
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

          {/* Avatar Builder */}
          <div>
            <label className="block text-cyan-300 font-mono mb-3 text-lg">
              ▶ PHYSICAL ATTRIBUTES:
            </label>
            <div className="flex flex-col md:flex-row gap-6 bg-cyan-400/5 border border-cyan-400 p-4">
              {/* Avatar Preview */}
              <div className="w-32 h-32 flex-shrink-0 border-2 border-cyan-400 overflow-hidden bg-black mx-auto md:mx-0">
                <img
                  src={generatedAvatarUrl}
                  alt="Avatar Preview"
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
              
              {/* Trait Selectors */}
              <div className="flex-1 grid grid-cols-2 gap-3 text-sm font-mono">
                <div>
                  <label className="block text-cyan-500 mb-1 text-xs">GENDER</label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full bg-black border border-cyan-400 text-cyan-300 p-2 focus:outline-none focus:ring-1 focus:ring-cyan-300"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="non-binary person">Non-Binary</option>
                  </select>
                </div>
                <div>
                  <label className="block text-cyan-500 mb-1 text-xs">SKIN TONE</label>
                  <select
                    value={skinTone}
                    onChange={(e) => setSkinTone(e.target.value)}
                    className="w-full bg-black border border-cyan-400 text-cyan-300 p-2 focus:outline-none focus:ring-1 focus:ring-cyan-300"
                  >
                    <option value="pale">Pale</option>
                    <option value="light">Light</option>
                    <option value="medium">Medium</option>
                    <option value="olive">Olive</option>
                    <option value="brown">Brown</option>
                    <option value="dark">Dark</option>
                  </select>
                </div>
                <div>
                  <label className="block text-cyan-500 mb-1 text-xs">HAIRSTYLE</label>
                  <select
                    value={hairstyle}
                    onChange={(e) => setHairstyle(e.target.value)}
                    className="w-full bg-black border border-cyan-400 text-cyan-300 p-2 focus:outline-none focus:ring-1 focus:ring-cyan-300"
                  >
                    <option value="short">Short</option>
                    <option value="long">Long</option>
                    <option value="curly">Curly</option>
                    <option value="messy">Messy</option>
                    <option value="bald">Bald</option>
                  </select>
                </div>
                <div>
                  <label className="block text-cyan-500 mb-1 text-xs">HAIR COLOR</label>
                  <select
                    value={hairColor}
                    onChange={(e) => setHairColor(e.target.value)}
                    className="w-full bg-black border border-cyan-400 text-cyan-300 p-2 focus:outline-none focus:ring-1 focus:ring-cyan-300"
                  >
                    <option value="black">Black</option>
                    <option value="brown">Brown</option>
                    <option value="blonde">Blonde</option>
                    <option value="red">Red</option>
                    <option value="blue">Blue</option>
                    <option value="pink">Pink</option>
                  </select>
                </div>
                <div>
                  <label className="block text-cyan-500 mb-1 text-xs">EYE COLOR</label>
                  <select
                    value={eyeColor}
                    onChange={(e) => setEyeColor(e.target.value)}
                    className="w-full bg-black border border-cyan-400 text-cyan-300 p-2 focus:outline-none focus:ring-1 focus:ring-cyan-300"
                  >
                    <option value="brown">Brown</option>
                    <option value="blue">Blue</option>
                    <option value="green">Green</option>
                    <option value="hazel">Hazel</option>
                  </select>
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
