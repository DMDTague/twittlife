"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-next';
import type { Session, User } from '@supabase/supabase-js';

/**
 * Auth Context
 * Manages user authentication and account state globally
 */

interface Account {
  id: string;
  username: string;
  current_generation: number;
  total_generations: number;
  peak_tier: string;
  current_handle: string;
}

interface Character {
  id: string;
  name: string;
  niche: string;
  generation: number;
  is_deplatformed: boolean;
  account_tier: string;
}

interface AuthContextType {
  // Auth state
  user: User | null;
  session: Session | null;
  loading: boolean;
  error: string | null;
  
  // Account state
  account: Account | null;
  character: Character | null;
  
  // Auth methods
  signUp: (email: string, password: string, username: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  
  // Character methods
  createCharacter: (handle: string, niche: string, stats: any) => Promise<void>;
  loadCharacter: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const supabase = createClientComponentClient();
  
  // Auth state
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Account state
  const [account, setAccount] = useState<Account | null>(null);
  const [character, setCharacter] = useState<Character | null>(null);

  // ============================================================================
  // Session Management
  // ============================================================================

  useEffect(() => {
    // Check for existing session on mount
    const checkSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session) {
          setSession(session);
          setUser(session.user);
          
          // Load account data if user exists
          if (session.user) {
            await loadAccountData(session.user.id);
          }
        }
      } catch (err) {
        console.error('Session check error:', err);
        setError('Failed to load session');
      } finally {
        setLoading(false);
      }
    };

    checkSession();

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, newSession) => {
      setSession(newSession);
      setUser(newSession?.user || null);
      
      if (newSession?.user) {
        await loadAccountData(newSession.user.id);
      } else {
        setAccount(null);
        setCharacter(null);
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, [supabase]);

  // ============================================================================
  // Helper Functions
  // ============================================================================

  const loadAccountData = useCallback(
    async (userId: string) => {
      try {
        // Fetch account from API
        const response = await fetch('/api/auth/current-character', {
          headers: {
            'Authorization': `Bearer ${session?.access_token || ''}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setAccount(data.account);
          
          // Extract character info from entity
          if (data.entity) {
            setCharacter({
              id: data.entity.id,
              name: data.entity.name,
              niche: data.entity.primary_niche,
              generation: data.game_state.generation_number,
              is_deplatformed: data.game_state.is_deplatformed,
              account_tier: data.entity.account_tier,
            });
          }
        }
      } catch (err) {
        console.error('Failed to load account data:', err);
      }
    },
    [session?.access_token]
  );

  // ============================================================================
  // Auth Methods
  // ============================================================================

  const signUp = useCallback(
    async (email: string, password: string, username: string) => {
      try {
        setError(null);
        
        const { data, error: signUpError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              username,
            },
          },
        });

        if (signUpError) {
          throw signUpError;
        }

        setUser(data.user);
        setSession(data.session);
      } catch (err: any) {
        const errorMessage = err?.message || 'Failed to sign up';
        setError(errorMessage);
        throw err;
      }
    },
    [supabase]
  );

  const signIn = useCallback(
    async (email: string, password: string) => {
      try {
        setError(null);

        const { data, error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (signInError) {
          throw signInError;
        }

        setSession(data.session);
        setUser(data.user);
      } catch (err: any) {
        const errorMessage = err?.message || 'Failed to sign in';
        setError(errorMessage);
        throw err;
      }
    },
    [supabase]
  );

  const signInWithGoogle = useCallback(async () => {
    try {
      setError(null);

      const { data, error: googleError } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (googleError) {
        throw googleError;
      }
    } catch (err: any) {
      const errorMessage = err?.message || 'Failed to sign in with Google';
      setError(errorMessage);
      throw err;
    }
  }, [supabase]);

  const signOut = useCallback(async () => {
    try {
      setError(null);

      const { error: signOutError } = await supabase.auth.signOut();
      if (signOutError) {
        throw signOutError;
      }

      setSession(null);
      setUser(null);
      setAccount(null);
      setCharacter(null);
    } catch (err: any) {
      const errorMessage = err?.message || 'Failed to sign out';
      setError(errorMessage);
      throw err;
    }
  }, [supabase]);

  // ============================================================================
  // Character Methods
  // ============================================================================

  const createCharacter = useCallback(
    async (handle: string, niche: string, stats: any) => {
      try {
        setError(null);

        if (!session?.access_token) {
          throw new Error('Not authenticated');
        }

        const response = await fetch('/api/auth/create-character', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({
            handle,
            niche,
            stats,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to create character');
        }

        // Reload character data
        await loadAccountData(user?.id || '');
      } catch (err: any) {
        const errorMessage = err?.message || 'Failed to create character';
        setError(errorMessage);
        throw err;
      }
    },
    [session?.access_token, user?.id, loadAccountData]
  );

  const loadCharacter = useCallback(async () => {
    if (user?.id) {
      await loadAccountData(user.id);
    }
  }, [user?.id, loadAccountData]);

  // ============================================================================
  // Provider Value
  // ============================================================================

  const value: AuthContextType = {
    user,
    session,
    loading,
    error,
    account,
    character,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
    createCharacter,
    loadCharacter,
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
