from pydantic import BaseModel, Field
from typing import Any, List, Dict, Literal, Optional

class LongTermMemory(BaseModel):
    core_beliefs: List[str] = Field(default_factory=list)
    grudges: List[str] = Field(default_factory=list)
    relationship_matrix: Dict[str, int] = Field(default_factory=dict) # map of entity_id -> score (-100 to 100)

class ShortTermMemory(BaseModel):
    current_mood: str = "Neutral"
    recent_interactions: List[str] = Field(default_factory=list) # List of event processing summaries or event IDs
    current_agenda: str = ""  # For Organization/Core agents pushing specific narratives

class TraitMatrix(BaseModel):
    politics: int = 0  # -100 (Extreme Left) to +100 (Extreme Right)
    tone: int = 0      # -100 (Troll/Irony) to +100 (Earnest/Literal)
    hostility: int = 0 # -100 (Passive/Agreeable) to +100 (Aggressive/Debate-bro)

class Demographics(BaseModel):
    gender: str = "Unspecified"
    sexuality: str = "Unspecified"

AgentTier = Literal['Basic', 'Core', 'Organization']

class Entity(BaseModel):
    id: str
    name: str
    primary_niche: str = "general" # e.g., "combat_sports", "tech", "gaming", "philly_local"
    bio: str = ""
    profile_image_url: str = ""
    private_description: str = ""
    is_player: bool = False
    follower_count: int = 1000 # Default starting aura/followers
    demographics: Demographics = Field(default_factory=Demographics)
    trait_matrix: TraitMatrix = Field(default_factory=TraitMatrix)
    archetype: str = "Standard"
    prompt_modifiers: str = "" # Specific instructions like "Speak strictly in polished PR statements"
    system_prompt_lock: str = "" # Strict personality override
    allowed_domains: List[str] = Field(default_factory=list) # Only tweet about these topics
    real_style_examples: List[str] = Field(default_factory=list) # Examples of real tweets to mimic style
    is_hacked: bool = False # If true, archetype/modifiers are temporarily overridden
    faction_tags: List[str] = Field(default_factory=list)
    agent_tier: AgentTier = "Basic"
    long_term_memory: LongTermMemory = Field(default_factory=LongTermMemory)
    short_term_memory: ShortTermMemory = Field(default_factory=ShortTermMemory)
    internal_truth: Dict[str, float] = Field(default_factory=dict) # The absolute truth for this NPC (-100 to 100)
    public_vibe: Dict[str, float] = Field(default_factory=dict)  # The perceived truth by the timeline, floats for smooth decay
    following: List[str] = Field(default_factory=list)
    blocked_list: List[str] = Field(default_factory=list)
    muted_list: List[str] = Field(default_factory=list)
    is_dogpiled: bool = False
    status: str = "Active"
    dogpile_end_time: float = 0.0
    
    # --- Economy & Verification (Phase 16) ---
    is_verified: bool = False
    simulated_credits: int = 0
    credits: int = 0  # God Mode currency for the banking API
    
    # --- Narrative Evolution (Phase 18) ---
    ratio_tracker: Dict[str, int] = Field(default_factory=dict)  # entity_id -> times ratioed by them
    is_rising_star: bool = False
    total_engagement: int = 0  # Cumulative likes + retweets received
    
    # --- Gamification (Phase 22) ---
    influence_rank: int = 1
    unlocked_achievements: List[str] = Field(default_factory=list)
    current_streak: int = 0
    rivalries: List[str] = Field(default_factory=list)
    aura: int = 1500
    alliance_scores: Dict[str, int] = Field(default_factory=dict) # titan_id -> score
    
    # --- Phase 24: Shadow Market & Strategy ---
    wealth: int = 0
    heat: int = 0 # 0-100
    vanguard_rank: Optional[int] = None
    shadowban_until: float = 0.0
    is_shadowbanned: bool = False
    recent_synthetic_growth: int = 0 # Tracks bots bought since last audit
    
    # --- Phase 24.1: Fandoms & Beefs ---
    aura_peak: int = 1500
    phi_fanaticism: float = 1.0 # Constant for Stan Shield strength
    toxicity_fatigue: int = 0
    hater_count: int = 0
    neutral_count: int = 0
    stan_count: int = 0
    active_beefs: List[str] = Field(default_factory=list) # List of target_ids currently in beef with
    momentum_buff_days: int = 0
    aura_debt_posts: int = 0
    is_griefing_account: bool = False
    unlocked_premium_avatars: bool = False
    monthly_income_breakdown: Dict[str, Any] = Field(default_factory=dict) # Phase 26: Supporter Pyramid
    last_payday_day: int = 0
    t1_supporters: int = 0
    t2_supporters: int = 0
    t3_supporters: int = 0
    last_known_follower_count: int = 0

VisibilityType = Literal['Public', 'Private', 'Sub-group']

class Event(BaseModel):
    id: str
    type: str # e.g. "tweet", "dm", "action"
    content: str
    initiator_id: str
    visibility: VisibilityType
    target_ids: List[str] = Field(default_factory=list) # for private or sub-group
    timestamp: float = 0.0
    impact_vectors: Dict[str, float] = Field(default_factory=dict) # Hidden LLM extracted metadata
    likes: List[str] = Field(default_factory=list) # List of entity IDs who liked
    retweets: List[str] = Field(default_factory=list) # List of entity IDs who retweeted
    reply_to_id: Optional[str] = None  # ID of parent tweet for threading
    replies_count: int = 0
    media_url: Optional[str] = None  # Phase 22 Media Engine

class GameState(BaseModel):
    entities: Dict[str, Entity] = Field(default_factory=dict)
    events: List[Event] = Field(default_factory=list)
