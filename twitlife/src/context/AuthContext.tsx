"use client";

import React, { createContext, useContext } from 'react';
import { useGameState, GameCharacter, LegacyData } from '@/hooks/useGameState';

/**
 * Auth Context - Thin wrapper around useGameState
 * Provides a unified character/auth interface for all pages.
 * No Supabase dependency — pure localStorage arcade mode.
 */

interface AuthContextType {
  // Character state
  character: GameCharacter | null;
  legacy: LegacyData | null;
  loading: boolean;

  // Convenience aliases for pages that reference "user"
  user: GameCharacter | null;

  // Character lifecycle
  createCharacter: (handle: string, niche: string, stats: { aura: number; heat: number; insight: number }, avatarUrl?: string) => GameCharacter;
  updateCharacter: (updates: Partial<GameCharacter>) => void;
  deplatform: (reason: string) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { character, legacy, loading, createCharacter, updateCharacter, deplatform, reset } = useGameState();

  const value: AuthContextType = {
    character,
    legacy,
    loading,
    user: character, // alias so pages checking `user` still work
    createCharacter,
    updateCharacter,
    deplatform,
    signOut: reset,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
