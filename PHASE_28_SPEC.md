# Phase 28: Player Journey (Auth + Onboarding + Game Over)

## Overview
Phase 28 transforms TwitLife from a stateless demo into a persistent, account-based game where players build dynasties across generations.

**Tech Stack:**
- Auth: Supabase Auth (Google OAuth + Email/Password)
- Database: PostgreSQL (Supabase)
- Caching: PostgreSQL native + Supabase Realtime
- Frontend: Next.js 14 + TypeScript + Supabase Client

---

## Phase 1A: Authentication & Account Creation

### 1.1 Database Schema Changes

#### `users` table (Supabase Auth managed)
- Tracks player metadata and progression
- Links to Supabase `auth.users`

```sql
CREATE TABLE public.accounts (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username VARCHAR(50) UNIQUE NOT NULL,
  is_player BOOLEAN DEFAULT true,
  current_handle VARCHAR(100),
  current_generation INT DEFAULT 1,
  total_generations INT DEFAULT 1,
  peak_tier VARCHAR(50) DEFAULT 'guest',
  total_wealth_accumulated INT DEFAULT 0,
  all_time_followers_peak INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Generation history table
CREATE TABLE public.account_generations (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  generation_number INT,
  handle VARCHAR(100),
  niche VARCHAR(50),
  starting_stats JSON, -- {aura, followers, wealth}
  ending_stats JSON,   -- {aura, followers, wealth, tier_reached}
  deplatform_reason VARCHAR(100),
  deplatform_date TIMESTAMP,
  legacy_aura_bonus INT,
  legacy_wealth_bonus INT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Main game state per generation
CREATE TABLE public.game_states (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  generation_number INT,
  player_entity_id VARCHAR(100),
  current_aura INT DEFAULT 1500,
  current_followers INT DEFAULT 500,
  current_wealth INT DEFAULT 0,
  current_tier VARCHAR(50) DEFAULT 'guest',
  tier_progress INT DEFAULT 0,
  is_deplatformed BOOLEAN DEFAULT false,
  deplatform_reason VARCHAR(255),
  status VARCHAR(50) DEFAULT 'active',
  last_action_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 1.2 Supabase Setup

```bash
# Install Supabase CLI
brew install supabase/tap/supabase

# Initialize (or link to existing project)
supabase init
supabase link

# Deploy migrations
supabase db push

# Generate TypeScript types
supabase gen types typescript --local > types/database.ts
```

### 1.3 Frontend Auth Flow

#### Component: `AuthContext` (React Context for global auth state)
```typescript
// src/context/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  account: Account | null;
  loading: boolean;
  signUp: (email: string, password: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  signInWithGoogle: () => Promise<void>;
}
```

#### Middleware: Protected Routes
```typescript
// src/middleware.ts
// Redirect unauthenticated users to /login
// Redirect authenticated users creating account to /create-account
```

#### Pages Tree:
```
/login                  → Login/Sign up page
/create-account         → Character creation screen
/dashboard              → Main game (protected)
/game-over             → Game over screen (protected)
/profile/[id]          → Profile page (public)
```

---

## Phase 1B: Character Creation Screen

### 2.1 Flow

**Step 1: Handle Selection**
- Input: Choose handle (must be unique in DB)
- Validation: 3-25 chars, alphanumeric + underscore
- API: `POST /api/auth/check-handle` → `{ available: boolean }`

**Step 2: Niche Selection (Radio buttons)**
- Options:
  - 🏴 **Combat Sports** (aggressive, tribalistic, fitness focused)
  - 💻 **Tech** (intellectual, contrarian, startup-focused)
  - 🏛️ **Politics** (polarized, ideological, current-events)
  - 🎮 **Gaming** (casual, community-focused, entertainment)
  - 📰 **General** (balanced, no niche bonus)

**Step 3: Stat Roll**
```
AURA (Charisma): 1-100     [You rolled: 67]
HEAT (Toxicity): 0-100     [You rolled: 34]
INSIGHT (IQ): 1-100        [You rolled: 72]

[Roll Again] [Accept]
```

- Player can re-roll up to 3 times
- Each niche gets +20 to one stat:
  - Combat Sports: +20 Heat
  - Tech: +20 Insight
  - Politics: +20 Heat AND -20 Aura reduction
  - Gaming: +20 Aura
  - General: No bonus

**Step 4: Review & Confirm**
- Display final character sheet
- Button: "Start Your Run"

### 2.2 Backend API

#### POST `/api/auth/create-character`
```json
{
  "handle": "string",
  "niche": "combat_sports|tech|politics|gaming|general",
  "stats": {
    "aura": 67,
    "heat": 34,
    "insight": 72
  }
}
```

**Response:**
```json
{
  "game_state_id": "uuid",
  "player_id": "entity_id",
  "starting_aura": 1587,  // 1500 base + 67 roll + niche bonus
  "starting_followers": 500,
  "starting_wealth": 0,
  "generation": 1
}
```

**Backend Logic:**
1. Create new `Entity` for player (in SQL)
2. Create new `GameState` entry for this generation
3. Initialize trait matrix based on selected niche
4. Apply tier = GUEST, shadowbanned = true (5 day grace period)
5. Return game state

### 2.3 Frontend Components

```typescript
// src/components/CharacterCreation/HandleStep.tsx
// Input validation, availability check

// src/components/CharacterCreation/NicheStep.tsx
// 5 radio button options with icons + descriptions

// src/components/CharacterCreation/StatRoll.tsx
// Display random stats, allow re-rolling

// src/components/CharacterCreation/ReviewStep.tsx
// Final confirmation with character sheet

// src/app/create-account/page.tsx
// Multi-step form orchestration
```

---

## Phase 1B: Game Over Screen

### 3.1 Trigger Conditions

When deplatformed:
1. Backend detects `check_deplatform_condition()` returns true
2. POST `/api/post_tweet` returns: `{ status: "deplatformed", stats: {...} }`
3. Frontend redirects to `/game-over?reason=toxicity_fatigue&tier=titan`

### 3.2 Screen Layout

```
┌─────────────────────────────────────────┐
│           [ACCOUNT TERMINATED]          │
│                                         │
│  Your run has ended.                    │
│  Thanks for playing.                    │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ FINAL STATS                     │   │
│  │ ─────────────────────────────── │   │
│  │ Highest Tier Reached: TITAN     │   │
│  │ Total Followers Peaked: 125,000 │   │
│  │ Total Wealth Accumulated: 45,320₵ │
│  │ Cause of Ban: Toxicity Fatigue  │   │
│  │ Days Active: 47d 12h            │   │
│  │ Posts Made: 348                 │   │
│  │ Total Engagement: 1,245,000     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ LEGACY BONUSES                  │   │
│  │ ─────────────────────────────── │   │
│  │ Generational Aura: +150         │   │
│  │ Generational Wealth: +21,660₵   │   │
│  │ Gen 2 Starting Followers: +1000  │   │
│  └─────────────────────────────────┘   │
│                                         │
│   [START NEXT GENERATION]               │
│   [View Account History]                │
│   [View Leaderboard]                    │
│   [Logout]                              │
└─────────────────────────────────────────┘
```

### 3.3 Backend API

#### GET `/api/game/final-stats?generation=1&user_id=uuid`
```json
{
  "character": {
    "handle": "@toxic_king_v2",
    "niche": "politics",
    "generation": 1,
    "account_tier": "titan",
    "deplatform_reason": "toxicity_fatigue",
    "deplatform_at": "2026-03-30T14:22:00Z"
  },
  "stats": {
    "aura_peak": 8750,
    "followers_peak": 125000,
    "wealth_accumulated": 45320,
    "posts_made": 348,
    "engagement_total": 1245000,
    "days_active": 47.5
  },
  "legacy": {
    "aura_bonus": 150,
    "wealth_bonus": 21660,
    "follower_bonus": 1000,
    "tier_bonus_multiplier": 1.1  // TITAN bonus
  }
}
```

#### POST `/api/game/new-generation` (Start next run)
```json
{
  "parent_generation": 1,
  "new_handle": "toxic_king_v3"
}
```

**Response:**
```json
{
  "generation": 2,
  "game_state_id": "uuid",
  "starting_aura": 1650,  // 1500 + 150 legacy
  "starting_followers": 1500,  // 500 + 1000 legacy
  "starting_wealth": 21660,  // Legacy wealth carry-over
  "legacy_bonuses_applied": true
}
```

### 3.4 Frontend Components

```typescript
// src/pages/game-over.tsx
// Main game over screen (protected route)

// src/components/GameOver/FinalStats.tsx
// Display character and performance stats

// src/components/GameOver/LegacyBonus.tsx
// Show inheritance for next generation

// src/components/GameOver/AccountHistory.tsx
// Timeline of all generations (bonus feature)
```

---

## Phase 1C: Character History & Archives

### 4.1 Account History Page

```
GET /api/user/account-history

Returns:
{
  "generations": [
    {
      "generation": 1,
      "handle": "@toxic_king_v1",
      "tier_reached": "titan",
      "followers_peak": 125000,
      "wealth_accumulated": 45320,
      "deplatform_reason": "toxicity_fatigue",
      "active_for_days": 47.5,
      "legacy_summary": "Controversial figure, massive following"
    },
    {
      "generation": 2,
      "handle": "@toxic_king_v2",
      "tier_reached": "verified",
      "followers_peak": 35000,
      "wealth_accumulated": 8900,
      "deplatform_reason": "crucible_failures",
      "active_for_days": 12,
      "legacy_summary": "Failed Crucible defense 3x"
    }
  ],
  "all_time_stats": {
    "generations_played": 2,
    "highest_tier": "titan",
    "highest_followers": 125000,
    "total_wealth_all_time": 54220
  }
}
```

---

## API Contracts Summary

### Auth Endpoints
- `POST /api/auth/signup` → Create Supabase user + account entry
- `POST /api/auth/login` → Supabase signin
- `POST /api/auth/logout` → Supabase signout
- `POST /api/auth/google` → OAuth flow
- `GET /api/auth/check-handle` → Validate username uniqueness

### Character Creation
- `POST /api/auth/check-handle?handle=username` → `{available: bool}`
- `POST /api/auth/create-character` → Initialize new character
- `GET /api/game/character-niche-data?niche=politics` → Bonus info for UI

### Game Over & Legacy
- `GET /api/game/final-stats?generation=1&user_id=uuid`
- `POST /api/game/new-generation` → Start next run with legacy bonuses
- `GET /api/user/account-history` → All generations history

### Main Game (Existing)
- `POST /api/post_tweet` → Now returns deplatforming status
- `GET /api/feed` → Protected by auth

---

## Database Migration Strategy

1. **Backup SQLite** → Export to CSV
2. **Create Supabase project**
3. **Run migrations** → Create schema
4. **Migrate NPC data** → Import from CSV
5. **Create Supabase Auth** → User table links
6. **Update FastAPI connection** → Use `supabase-py` client
7. **Test end-to-end** → Auth → Create character → Play

---

## Implementation Order

### Week 1: Foundation
- [ ] Set up Supabase project + PostgreSQL schema
- [ ] Create Supabase Auth (email + Google OAuth)
- [ ] Build AuthContext + middleware
- [ ] Implement `/login` page (Supabase form components)

### Week 2: Character Creation
- [ ] Build character creation multi-step form
- [ ] API endpoints for handle validation & character init
- [ ] Redirect authenticated users to `/create-account`
- [ ] Test character creation end-to-end

### Week 3: Game Over & Legacy
- [ ] Build game-over screen template
- [ ] Implement final-stats API
- [ ] Test deplatforming → game-over flow
- [ ] Implement "Start Next Generation" logic

### Week 4: Polish & Integration
- [ ] Account history page
- [ ] Migrate SQLite data to PostgreSQL
- [ ] End-to-end testing with real users
- [ ] Deploy to production

---

## Success Criteria

✅ **Authentication Works**
- Players can sign up / log in
- Google OAuth works
- Sessions persist across page reloads

✅ **Character Creation Works**
- Handle validation prevents duplicates
- Stat roll system is fair and visible
- Niche selection affects starting stats
- Player enters game with correct bonuses

✅ **Game Over Flow Works**
- Deplatforming triggers game-over screen
- Final stats display correctly
- Legacy bonuses calculate accurately
- "Start Next Generation" saves properly

✅ **Account Persistence**
- Multiple generations saved to database
- History page shows all runs
- Legacy bonuses carry over

---

## Notes

- **Supabase Realtime** for future multiplayer leaderboards
- **Supabase Edge Functions** for rate limiting (future)
- **PostgSQL JSONB** for storing complex data (trait matrices, memories)
- **Supabase Row-Level Security (RLS)** to prevent players accessing other accounts
