"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useGameState } from "@/hooks/useGameState";
import { useAudio } from "@/hooks/useAudio";

export default function DeathScreen() {
  const router = useRouter();
  const gameState = useGameState();
  const { gameOver } = useAudio();

  // On mount, play game over sound
  useEffect(() => {
    gameOver();
  }, [gameOver]);

  // Death animation - black fade in
  useEffect(() => {
    const timer = setTimeout(() => {
      // After brief delay, show the tombstone
      // (This happens via CSS animation)
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const handleNextGen = () => {
    router.push("/");
  };

  const handleReplay = () => {
    gameState.reset();
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-black overflow-hidden relative">
      {/* Black fade animation */}
      <div
        className="absolute inset-0 bg-black animate-in fade-in duration-1000"
        style={{
          animation: "fadeIn 1s ease-out forwards",
        }}
      />

      {/* Tombstone / Game Over Card */}
      <div
        className="relative z-10 min-h-screen flex items-center justify-center px-4"
        style={{
          animation: "tombstoneAppear 2s ease-out 1s forwards",
          opacity: 0,
        }}
      >
        <div className="max-w-2xl w-full space-y-8">
          {/* Death Banner */}
          <div className="text-center space-y-4 mb-12">
            <div className="text-6xl mb-4">⚰️</div>
            <h1 className="text-6xl font-black text-white font-serif tracking-wider">
              ACCOUNT TERMINATED
            </h1>
          </div>

          {/* Tombstone */}
          <div className="border-8 border-gray-600 bg-gray-800 relative p-12 shadow-2xl">
            {/* Tombstone shape top */}
            <div
              className="absolute -top-12 left-1/2 transform -translate-x-1/2"
              style={{
                width: 0,
                height: 0,
                borderLeft: "50px solid transparent",
                borderRight: "50px solid transparent",
                borderBottom: "60px solid rgb(31, 41, 55)",
              }}
            />

            {/* RIP Text */}
            <div className="text-center space-y-8">
              <div className="text-white font-serif space-y-2">
                <p className="text-4xl font-bold">R.I.P</p>
              </div>

              {/* Stats Display - Epitaph */}
              <div className="bg-black/50 border-2 border-gray-500 p-8 space-y-4 text-center">
                <div>
                  <p className="text-gray-400 text-sm mb-1">HANDLE</p>
                  <p className="text-white text-2xl font-bold font-mono">
                    {gameState.legacy?.handle}
                  </p>
                </div>

                <div className="border-t border-gray-600 pt-4">
                  <p className="text-gray-400 text-sm mb-1">GENERATION</p>
                  <p className="text-amber-400 text-xl font-bold">
                    Gen {gameState.legacy?.generation}
                  </p>
                </div>

                <div className="border-t border-gray-600 pt-4">
                  <p className="text-gray-400 text-sm mb-1">CAUSE OF BAN</p>
                  <p className="text-red-400 text-lg font-bold uppercase">
                    {gameState.legacy?.cause.replace(/_/g, " ")}
                  </p>
                </div>

                <div className="border-t border-gray-600 pt-4">
                  <p className="text-gray-400 text-sm mb-1">TIER REACHED</p>
                  <p className="text-purple-400 text-xl font-bold">
                    {gameState.legacy?.tierReached}
                  </p>
                </div>
              </div>

              {/* Legacy Bonus Display */}
              {gameState.legacy && (
                <div className="bg-amber-400/20 border-2 border-amber-400 p-6">
                  <p className="text-amber-300 font-bold text-sm mb-3">
                    ✨ LEGACY CARRIES ON ✨
                  </p>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-cyan-300 text-sm">AURA BONUS</p>
                      <p className="text-cyan-400 text-xl font-bold">
                        +{gameState.legacy.auraBonus}
                      </p>
                    </div>
                    <div>
                      <p className="text-green-300 text-sm">WEALTH BONUS</p>
                      <p className="text-green-400 text-xl font-bold">
                        +{gameState.legacy.wealthBonus}
                      </p>
                    </div>
                    <div>
                      <p className="text-purple-300 text-sm">FOLLOWER BONUS</p>
                      <p className="text-purple-400 text-xl font-bold">
                        +{gameState.legacy.followerBonus}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Epitaph */}
              <div className="text-gray-400 font-serif italic text-sm space-y-2 pt-4">
                <p>"They rose. They fell."</p>
                <p>"The algorithm is eternal."</p>
              </div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex gap-4 justify-center pt-8">
            <button
              onClick={handleNextGen}
              className="bg-cyan-500 hover:bg-cyan-400 text-black font-black py-4 px-8 rounded-lg text-lg transition-all transform hover:scale-105 active:scale-95"
            >
              ▶ CONTINUE LEGACY
            </button>

            <button
              onClick={handleReplay}
              className="bg-gray-700 hover:bg-gray-600 text-white font-black py-4 px-8 rounded-lg text-lg transition-all"
            >
              ◀ RETRY
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes tombstoneAppear {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
