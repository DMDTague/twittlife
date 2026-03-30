-- Phase 28: Supabase Database Schema
-- Run these migrations in order

-- 001_create_accounts_table.sql
CREATE TABLE IF NOT EXISTS public.accounts (
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

CREATE INDEX idx_accounts_username ON accounts(username);
CREATE INDEX idx_accounts_created_at ON accounts(created_at);

-- Enable RLS
ALTER TABLE public.accounts ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own account
CREATE POLICY "Users can view own account"
  ON public.accounts FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own account"
  ON public.accounts FOR UPDATE
  USING (auth.uid() = id);

-- 002_create_account_generations_table.sql
CREATE TABLE IF NOT EXISTS public.account_generations (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES accounts(id) ON DELETE CASCADE NOT NULL,
  generation_number INT NOT NULL,
  handle VARCHAR(100) NOT NULL,
  niche VARCHAR(50) NOT NULL,
  starting_stats JSONB DEFAULT '{"aura": 0, "followers": 0, "wealth": 0}',
  ending_stats JSONB DEFAULT '{"aura": 0, "followers": 0, "wealth": 0, "tier": "guest"}',
  deplatform_reason VARCHAR(100),
  deplatform_date TIMESTAMP,
  legacy_aura_bonus INT DEFAULT 0,
  legacy_wealth_bonus INT DEFAULT 0,
  legacy_follower_bonus INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, generation_number)
);

CREATE INDEX idx_generations_user_id ON account_generations(user_id);
CREATE INDEX idx_generations_generation_number ON account_generations(generation_number);

ALTER TABLE public.account_generations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own generations"
  ON public.account_generations FOR SELECT
  USING (user_id = auth.uid());

-- 003_create_game_states_table.sql
CREATE TABLE IF NOT EXISTS public.game_states (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES accounts(id) ON DELETE CASCADE NOT NULL,
  generation_number INT NOT NULL,
  player_entity_id VARCHAR(100) NOT NULL,
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
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, generation_number)
);

CREATE INDEX idx_game_states_user_id ON game_states(user_id);
CREATE INDEX idx_game_states_player_entity_id ON game_states(player_entity_id);
CREATE INDEX idx_game_states_status ON game_states(status);

ALTER TABLE public.game_states ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own game state"
  ON public.game_states FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Users can update own game state"
  ON public.game_states FOR UPDATE
  USING (user_id = auth.uid());

-- 004_create_entities_table.sql
-- Migrated from SQLite models.py
CREATE TABLE IF NOT EXISTS public.entities (
  id VARCHAR(100) PRIMARY KEY,
  user_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
  name VARCHAR(255) NOT NULL,
  primary_niche VARCHAR(50) DEFAULT 'general',
  bio TEXT DEFAULT '',
  profile_image_url TEXT DEFAULT '',
  private_description TEXT DEFAULT '',
  is_player BOOLEAN DEFAULT false,
  follower_count INT DEFAULT 1000,
  demographics JSONB DEFAULT '{"gender": "Unspecified", "sexuality": "Unspecified"}',
  trait_matrix JSONB DEFAULT '{"politics": 0, "tone": 0, "hostility": 0}',
  archetype VARCHAR(100) DEFAULT 'Standard',
  prompt_modifiers TEXT DEFAULT '',
  system_prompt_lock TEXT DEFAULT '',
  allowed_domains TEXT[] DEFAULT '{}',
  real_style_examples TEXT[] DEFAULT '{}',
  is_hacked BOOLEAN DEFAULT false,
  faction_tags TEXT[] DEFAULT '{}',
  agent_tier VARCHAR(50) DEFAULT 'Basic',
  long_term_memory JSONB DEFAULT '{"core_beliefs": [], "grudges": [], "relationship_matrix": {}}',
  short_term_memory JSONB DEFAULT '{"current_mood": "Neutral", "recent_interactions": [], "current_agenda": ""}',
  internal_truth JSONB DEFAULT '{}',
  public_vibe JSONB DEFAULT '{}',
  following TEXT[] DEFAULT '{}',
  blocked_list TEXT[] DEFAULT '{}',
  muted_list TEXT[] DEFAULT '{}',
  is_dogpiled BOOLEAN DEFAULT false,
  status VARCHAR(50) DEFAULT 'Active',
  dogpile_end_time DOUBLE PRECISION DEFAULT 0.0,
  is_verified BOOLEAN DEFAULT false,
  simulated_credits INT DEFAULT 0,
  credits INT DEFAULT 0,
  ratio_tracker JSONB DEFAULT '{}',
  is_rising_star BOOLEAN DEFAULT false,
  total_engagement INT DEFAULT 0,
  influence_rank INT DEFAULT 1,
  unlocked_achievements TEXT[] DEFAULT '{}',
  current_streak INT DEFAULT 0,
  rivalries TEXT[] DEFAULT '{}',
  aura INT DEFAULT 1500,
  alliance_scores JSONB DEFAULT '{}',
  wealth INT DEFAULT 0,
  heat INT DEFAULT 0,
  vanguard_rank INT,
  shadowban_until DOUBLE PRECISION DEFAULT 0.0,
  is_shadowbanned BOOLEAN DEFAULT false,
  recent_synthetic_growth INT DEFAULT 0,
  aura_peak INT DEFAULT 1500,
  phi_fanaticism DOUBLE PRECISION DEFAULT 1.0,
  -- Phase 27 additions
  account_tier VARCHAR(50) DEFAULT 'guest',
  tier_progress INT DEFAULT 0,
  crucible_failures INT DEFAULT 0,
  is_deplatformed BOOLEAN DEFAULT false,
  deplatform_reason VARCHAR(255),
  legacy_generation INT DEFAULT 0,
  legacy_aura_bonus INT DEFAULT 0,
  generational_wealth INT DEFAULT 0,
  total_influence_score INT DEFAULT 0,
  job_status VARCHAR(50) DEFAULT 'unemployed',
  job_start_date TIMESTAMP,
  salary_per_day INT DEFAULT 0,
  follower_growth_rate DOUBLE PRECISION DEFAULT 0.0,
  engagement_multiplier DOUBLE PRECISION DEFAULT 1.0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_entities_user_id ON entities(user_id);
CREATE INDEX idx_entities_is_player ON entities(is_player);
CREATE INDEX idx_entities_is_deplatformed ON entities(is_deplatformed);
CREATE INDEX idx_entities_account_tier ON entities(account_tier);

ALTER TABLE public.entities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public entities visible to all"
  ON public.entities FOR SELECT
  USING (true);

-- Only allow updates to own player entity
CREATE POLICY "Players can update own entity"
  ON public.entities FOR UPDATE
  USING (user_id = auth.uid() AND is_player = true);

-- 005_create_events_table.sql
CREATE TABLE IF NOT EXISTS public.events (
  id VARCHAR(100) PRIMARY KEY,
  entity_id VARCHAR(100) REFERENCES entities(id) ON DELETE CASCADE,
  event_type VARCHAR(100),
  text TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  engagement_score INT DEFAULT 0,
  reply_chain TEXT[] DEFAULT '{}',
  is_player_event BOOLEAN DEFAULT false,
  sentiment_score INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_entity_id ON events(entity_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_is_player_event ON events(is_player_event);

ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public events visible to all" ON public.events FOR SELECT USING (true);
