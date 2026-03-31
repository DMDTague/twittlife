"use client";

import { useCallback, useState, useEffect } from "react";

export interface GameCharacter {
  id: string;
  handle: string;
  niche: string;
  generation: number;
  aura: number;
  wealth: number;
  heat: number;
  followers: number;
  accountTier: string;
  createdAt: number;
  avatarUrl?: string;
}

export interface LegacyData {
  handle: string;
  generation: number;
  auraBonus: number;
  wealthBonus: number;
  followerBonus: number;
  tierReached: string;
  cause: string;
}

const STORAGE_KEY = "twitlife_character";
const LEGACY_KEY = "twitlife_legacy";

/**
 * Pure localStorage-based game state manager
 * No auth required - just pure arcade fun
 */
export function useGameState() {
  const [character, setCharacter] = useState<GameCharacter | null>(null);
  const [legacy, setLegacy] = useState<LegacyData | null>(null);
  const [loading, setLoading] = useState(true);

  // ============================================================================
  // Load State on Mount
  // ============================================================================

  useEffect(() => {
    const loadState = () => {
      try {
        // Load current character
        const charData = localStorage.getItem(STORAGE_KEY);
        if (charData) {
          setCharacter(JSON.parse(charData));
        }

        // Load legacy data (if available)
        const legacyData = localStorage.getItem(LEGACY_KEY);
        if (legacyData) {
          setLegacy(JSON.parse(legacyData));
        }
      } catch (err) {
        console.error("Failed to load game state:", err);
      } finally {
        setLoading(false);
      }
    };

    loadState();
  }, []);

  // ============================================================================
  // Create Character
  // ============================================================================

  const createCharacter = useCallback(
    (handle: string, niche: string, stats: { aura: number; heat: number; insight: number }, avatarUrl?: string) => {
      const id = `char_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      const newCharacter: GameCharacter = {
        id,
        handle,
        niche,
        generation: legacy ? (legacy as any).generation + 1 : 1,
        aura: 1500 + stats.aura + (legacy?.auraBonus || 0),
        wealth: legacy?.wealthBonus || 0,
        heat: stats.heat,
        followers: 500 + (legacy?.followerBonus || 0),
        accountTier: "guest",
        createdAt: Date.now(),
        avatarUrl,
      };

      localStorage.setItem(STORAGE_KEY, JSON.stringify(newCharacter));

      // Clear legacy after using it
      localStorage.removeItem(LEGACY_KEY);
      setLegacy(null);

      setCharacter(newCharacter);
      return newCharacter;
    },
    [legacy]
  );

  // ============================================================================
  // Save Character State
  // ============================================================================

  const updateCharacter = useCallback((updates: Partial<GameCharacter>) => {
    setCharacter((prev) => {
      if (!prev) return null;
      const updated = { ...prev, ...updates };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  // ============================================================================
  // Game Over / Deplatforming
  // ============================================================================

  const deplatform = useCallback(
    (reason: string) => {
      if (!character) return;

      // Save legacy data (10% inheritance as mentioned)
      const legacyData: LegacyData = {
        handle: character.handle,
        generation: character.generation,
        auraBonus: Math.floor(character.aura * 0.1),
        wealthBonus: Math.floor(character.wealth * 0.1),
        followerBonus: Math.floor(character.followers * 0.1),
        tierReached: character.accountTier,
        cause: reason,
      };

      localStorage.setItem(LEGACY_KEY, JSON.stringify(legacyData));
      localStorage.removeItem(STORAGE_KEY);

      setCharacter(null);
      setLegacy(legacyData);
    },
    [character]
  );

  // ============================================================================
  // Clear Everything
  // ============================================================================

  const reset = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(LEGACY_KEY);
    setCharacter(null);
    setLegacy(null);
  }, []);

  return {
    character,
    legacy,
    loading,
    createCharacter,
    updateCharacter,
    deplatform,
    reset,
  };
}
