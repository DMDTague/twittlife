# TwitLife → BitLife: Technical Implementation Guide

## 🎮 Current State Assessment
✅ **Already Built:**
- Relationship matrix (entity_id → score -100 to 100)
- Memory systems (long/short term)
- Toxicity fatigue tracking
- Simulation eras (Peace, Bloodbath, Purge)
- Autonomous chaos daemon
- Crucible event templates
- SQLite persistence
- Faction warfare scaffold

❌ **Missing Systems (Priority Order):**
1. Account lifecycle (tiers, deplatforming, legacy)
2. NPC career evolution & auto-replies
3. Dynamic world events (Hater Winter, Algorithmic Shifts)
4. God Mode enhancements (Propaganda, Edit Truth, Leaks)
5. Frontend juiciness (stat floats, sound effects)

---

## 1️⃣ ACCOUNT LIFECYCLE: The Game-Over Mechanic

### 1.1 Account Tier System
**File: `models.py`** - Add to Entity:
```python
class AccountTier(str, Enum):
    GUEST = "guest"           # Start here, shadowbanned
    VERIFIED = "verified"     # Earned through 5 main-line quests
    TITAN = "titan"           # 50k+ followers (current max tier)
    LEGACY = "legacy"         # Retired/banned account (monuments only)

class Entity(BaseModel):
    # ... existing fields ...
    
    # Account Lifecycle (NEW)
    account_tier: AccountTier = AccountTier.GUEST
    tier_progress: int = 0        # 0-100, for verified progression
    crucible_failures: int = 0    # Increments on failed crucibles (game over at 3)
    is_deplatformed: bool = False # Game over state
    deplatform_reason: Optional[str] = None
    legacy_generation: int = 0    # 0 = original, 1 = after first ban/retire
    legacy_aura_bonus: int = 0    # Inherited from previous account
    generational_wealth: int = 0  # Wealth carries forward
    total_influence_score: float = 0.0  # Sum of all engagement (for legacy)
```

**File: `engine.py`** - Add deplatforming trigger:
```python
def check_deplatform_condition(self, entity: Entity) -> bool:
    """
    Game Over triggers:
    1. toxicity_fatigue >= 100
    2. crucible_failures >= 3
    3. Executive deplatforming from world events
    """
    if entity.toxicity_fatigue >= 100:
        return True
    if entity.crucible_failures >= 3:
        return True
    return False

def trigger_deplatforming(self, entity: Entity, reason: str):
    """
    Player is banned. Execute graceful restart flow.
    """
    # Save legacy data
    entity.legacy_generation += 1
    entity.total_influence_score += entity.aura + entity.follower_count/100
    entity.legacy_aura_bonus = int(entity.total_influence_score * 0.1)  # 10% carries over
    entity.generational_wealth = int(entity.wealth * 0.5)              # 50% wealth carries
    
    # Mark as deplatformed
    entity.is_deplatformed = True
    entity.deplatform_reason = reason
    entity.status = "Deplatformed"
    
    # Log to event stream for UI notification
    event = Event(
        id=str(uuid.uuid4()),
        type="deplatform",
        timestamp=time.time(),
        protagonist_id=entity.id,
        content_summary=f"Account deplatformed: {reason}",
        impact={"legacy_bonus": entity.legacy_aura_bonus}
    )
    self.state.events.append(event)
    
    return event

def start_new_account(self, old_account: Entity, new_handle: str) -> Entity:
    """
    Player clicks "New Life." Create fresh account with legacy bonuses.
    """
    new_entity = Entity(
        id=str(uuid.uuid4()),
        name=new_handle,
        account_tier=AccountTier.GUEST,
        aura=500 + old_account.legacy_aura_bonus,  # Starter pack + bonus
        wealth=old_account.generational_wealth,
        is_shadowbanned=True,  # All guest accounts start shadowbanned
        shadowban_until=time.time() + 86400 * 3,  # 3 days
        legacy_generation=old_account.legacy_generation,
        total_influence_score=0
    )
    self.add_entity(new_entity)
    return new_entity
```

### 1.2 Guest → Verified Progression Quest
**File: `gamification.py`** - Add tier quest system:
```python
TIER_PROGRESSION_QUESTS = {
    "verified": [
        {
            "id": "first_1k",
            "desc": "Reach 1,000 followers",
            "condition": lambda e: e.follower_count >= 1000,
            "reward": 1
        },
        {
            "id": "post_10_days",
            "desc": "Post at least once for 10 consecutive days",
            "condition": lambda e: getattr(e, 'days_active_streak', 0) >= 10,
            "reward": 1
        },
        {
            "id": "survive_crucible",
            "desc": "Survive a Crucible (fail < 3 times)",
            "condition": lambda e: e.crucible_failures == 0,
            "reward": 1
        },
        {
            "id": "post_viral",
            "desc": "Get a post to 10k+ engagement",
            "condition": lambda e: getattr(e, 'best_post_engagement', 0) >= 10000,
            "reward": 2
        },
        {
            "id": "build_alliance",
            "desc": "Build +50 relationship with 3 NPCs",
            "condition": lambda e: sum(1 for s in e.long_term_memory.relationship_matrix.values() if s >= 50) >= 3,
            "reward": 1
        }
    ]
}

def check_tier_progression(entity: Entity) -> int:
    """
    Returns progress (0-5) for verified tier. At 5/5, tier unlocked.
    """
    if entity.account_tier != AccountTier.GUEST:
        return -1  # Already verified
    
    tier_progress = entity.tier_progress or 0
    quests = TIER_PROGRESSION_QUESTS["verified"]
    
    for quest in quests:
        if quest["condition"](entity):
            tier_progress += quest["reward"]
    
    entity.tier_progress = tier_progress
    
    if tier_progress >= 5:
        entity.account_tier = AccountTier.VERIFIED
        entity.is_shadowbanned = False
        entity.shadowban_until = 0.0
        print(f"[TIER UP] {entity.name} is now VERIFIED!")
    
    return tier_progress
```

---

## 2️⃣ NPC CAREER EVOLUTION & AUTO-REPLIES

### 2.1 NPC Career Paths
**File: `models.py`** - Add to Entity:
```python
class JobStatus(str, Enum):
    STREAMING="streaming"
    TRADING="trading"
    JOURNALISM="journalism"
    ACADEMIA="academia"
    POLITICS="politics"
    CORPORATE="corporate"
    UNEMPLOYED="unemployed"
    CANCELLED="cancelled"

class Entity(BaseModel):
    # ... existing fields ...
    
    # Career (NEW)
    job_status: JobStatus = JobStatus.STREAMING
    job_start_date: int = 0  # Day job began
    years_in_job: float = 0.0
    salary_per_day: int = 100
    is_laid_off: bool = False
    
    # Career progression
    follower_growth_rate: float = 1.0  # Multiplier on organic growth
    engagement_multiplier: float = 1.0  # How viral their posts are
```

**File: `engine.py`** - Add NPC career simulation:
```python
def simulate_npc_career_day(self, npc: Entity):
    """
    Daily career progression for NPCs.
    Jobs grow followers, get cancelled, change roles.
    """
    import random
    
    if npc.is_player or npc.agent_tier == "Basic":
        return  # Only for Core/Organization NPCs
    
    # Organic follower decay if unemployed
    if npc.job_status == JobStatus.UNEMPLOYED:
        decay = int(npc.follower_count * 0.02)  # Lose 2% daily
        npc.follower_count = max(100, npc.follower_count - decay)
        npc.engagement_multiplier *= 0.95  # Engagement fades
    
    # Job change chance (every 30 days)
    if random.random() < 0.03:  # ~3% chance = once per month
        old_job = npc.job_status
        new_job = random.choice([j for j in JobStatus if j != old_job])
        npc.job_status = new_job
        npc.years_in_job = 0
        
        # Job change affects stats
        if new_job == JobStatus.CANCELLED:
            npc.follower_count = int(npc.follower_count * 0.3)  # Lose 70% followers
            npc.engagement_multiplier = 0.1
            npc.is_shadowbanned = True
        elif new_job == JobStatus.STREAMING:
            npc.salary_per_day = 500
            npc.follower_growth_rate = 1.5
        
        print(f"[NPC CAREER] {npc.name} → {new_job.value}")
    
    # Salary earned
    npc.wealth = getattr(npc, 'wealth', 0) + npc.salary_per_day
    npc.years_in_job += 1.0 / 365.0
```

### 2.2 Relationship-Based Auto-Replies
**File: `engine.py`** - Add auto-reply generator:
```python
def generate_auto_replies(self, post_event: Event, player: Entity) -> list[Event]:
    """
    When player posts, haters/lovers auto-reply based on relationship.
    Haters with -80+ relationship auto-reply with toxicity.
    """
    auto_reply_events = []
    
    for npc_id, relationship_score in player.long_term_memory.relationship_matrix.items():
        npc = self.state.entities.get(npc_id)
        if not npc or npc.is_player:
            continue
        
        # Hate threshold: auto-reply with negativity
        if relationship_score <= -80 and random.random() < 0.6:  # 60% chance
            aggressive_reply = self.generate_autonomous_post(
                npc, 
                topic=post_event.primary_topic,
                force_tone="aggressive"
            )
            if aggressive_reply:
                aggressive_reply.is_quote_retweet = True
                aggressive_reply.quotes_post_id = post_event.id
                auto_reply_events.append(aggressive_reply)
                
                # Update relationship (further down dive after aggressive comment)
                npc.long_term_memory.relationship_matrix[player.id] = int(relationship_score * 1.05)
        
        # Love threshold: auto-reply with support
        elif relationship_score >= 80 and random.random() < 0.4:
            supportive_reply = self.generate_autonomous_post(
                npc,
                topic=post_event.primary_topic,
                force_tone="supportive"
            )
            if supportive_reply:
                supportive_reply.is_quote_retweet = True
                auto_reply_events.append(supportive_reply)
    
    return auto_reply_events

def update_relationship_decay(self, entity: Entity):
    """
    Relationships decay over time if no interaction.
    """
    for npc_id in list(entity.long_term_memory.relationship_matrix.keys()):
        current_score = entity.long_term_memory.relationship_matrix[npc_id]
        
        # Decay towards neutral (0)
        if current_score > 0:
            entity.long_term_memory.relationship_matrix[npc_id] = int(current_score * 0.98)
        elif current_score < 0:
            entity.long_term_memory.relationship_matrix[npc_id] = int(current_score * 0.98)
```

---

## 3️⃣ SYSTEMIC WORLD EVENTS

### 3.1 Hater Winter Event
**File: `engine.py`** - Add event system:
```python
def trigger_hater_winter(self):
    """
    Random event: All NPCs' hostility +50% for 7 days.
    """
    duration_days = 7
    self.state.active_events.append({
        "type": "hater_winter",
        "start_day": self.current_day,
        "end_day": self.current_day + duration_days,
        "effect": {
            "hostility_boost": 0.5,
            "heat_generation_mult": 2.0
        }
    })
    
    # Boost all NPCs hostility
    for npc in self.state.entities.values():
        if not npc.is_player:
            npc.trait_matrix.hostility = int(min(100, npc.trait_matrix.hostility * 1.5))
    
    print(f"[WORLD EVENT] Hater Winter begins for {duration_days} days!")

def get_active_world_modifiers(self) -> dict:
    """
    Return current world event multipliers.
    """
    modifiers = {
        "hostility_mult": 1.0,
        "heat_mult": 1.0,
        "engagement_mult": 1.0
    }
    
    for event in self.state.active_events:
        if self.current_day <= event["end_day"]:
            for key, value in event["effect"].items():
                if key in modifiers:
                    modifiers[key] *= value
    
    return modifiers
```

### 3.2 Algorithmic Shifts
**File: `engine.py`** - Add topic reach variance:
```python
def trigger_algorithmic_shift(self):
    """
    Every 5 days, algorithm changes topic reach multipliers.
    E.g., Tech posts get 0x reach, Combat Sports get 10x.
    """
    topics = ["tech", "combat_sports", "politics", "gaming", "philly_local", "finance"]
    shifts = {topic: random.uniform(0.1, 3.0) for topic in topics}
    
    self.state.algorithmic_topic_multipliers = shifts
    print(f"[ALGORITHM] Shifts triggered: {shifts}")

def get_topic_reach_multiplier(self, topic: str) -> float:
    """
    Fetch current algorithmic multiplier for topic.
    """
    return self.state.algorithmic_topic_multipliers.get(topic, 1.0)
```

### 3.3 NPC Faction Wars (Autonomous)
**File: `engine.py`** - Enhance existing faction warfare:
```python
def orchestrate_faction_warfare(self):
    """
    Existing method - enhance to generate actual conflicts.
    """
    # Get faction leaders
    main_line = [e for e in self.state.entities.values() 
                 if "Main Line Influencers" in e.faction_tags and not e.is_player]
    delco_trolls = [e for e in self.state.entities.values() 
                    if "Delco Trolls" in e.faction_tags and not e.is_player]
    
    if not main_line or not delco_trolls:
        return []
    
    # Pick random combatants
    attacker = random.choice(main_line)
    defender = random.choice(delco_trolls)
    
    # Generate quote-tweet chain (existing follower_migration logic)
    events = []
    for i in range(3):  # 3-post escalation
        post = self.generate_autonomous_post(
            attacker if i % 2 == 0 else defender,
            topic="politics",
            force_tone="aggressive"
        )
        if post:
            events.append(post)
    
    return events
```

---

## 4️⃣ GOD MODE ENHANCEMENTS

### 4.1 Propaganda Machine
**File: `engine.py`** - Add to game mechanics:
```python
def propaganda_machine(self, player: Entity, target_npc_id: str, custom_prompt: str) -> bool:
    """
    Player spends Wealth to control NPC's posts for 24 hours.
    Cost: 50 wealth credits
    """
    if player.wealth < 50:
        return False
    
    target = self.state.entities.get(target_npc_id)
    if not target:
        return False
    
    # Store original prompt
    target.original_system_prompt = target.system_prompt_lock
    
    # Override with custom
    target.system_prompt_lock = custom_prompt
    target.controlled_by_player_until = time.time() + 86400  # 24 hours
    
    player.wealth -= 50
    
    print(f"[PROPAGANDA] {player.name} controls {target.name} for 24h")
    return True
```

### 4.2 Edit Internal Truth
**File: `models.py`** - Add to Entity:
```python
class Entity(BaseModel):
    # ... existing ...
    internal_truth_editable: bool = False  # Unlock in god mode
    internal_truth_last_edit: Optional[str] = None
    internal_truth_edit_count: int = 0
```

**File: `engine.py`:**
```python
def reveal_internal_truth(self, player: Entity, target_npc_id: str) -> dict:
    """
    Player pays Aura to see NPC's true beliefs/prompts.
    """
    cost = 100  # Aura cost
    if player.aura < cost:
        return {"error": "Not enough aura"}
    
    target = self.state.entities.get(target_npc_id)
    truth = {
        "system_prompt": target.system_prompt_lock[:100] + "...",
        "core_beliefs": target.long_term_memory.core_beliefs[:5],
        "grudges": target.long_term_memory.grudges[:3],
        "real_stances": target.internal_truth
    }
    
    player.aura -= cost
    return truth

def edit_internal_truth_word(self, player: Entity, target_npc_id: str, key: str, old_word: str, new_word: str) -> bool:
    """
    Player rewrites one word in NPC's belief system.
    E.g., change "Phil's biggest fan" → "Phil's worst nightmare"
    """
    cost = 200  # High Aura cost
    if player.aura < cost:
        return False
    
    target = self.state.entities.get(target_npc_id)
    if not target:
        return False
    
    # Find and replace word in internal_truth
    if key in target.internal_truth:
        old_val = str(target.internal_truth[key])
        if old_word in old_val:
            new_val = old_val.replace(old_word, new_word)
            target.internal_truth[key] = new_val
            player.aura -= cost
            
            # Track edit
            target.internal_truth_edit_count += 1
            target.internal_truth_last_edit = new_val
            
            print(f"[EDIT TRUTH] Altered {target.name}'s belief")
            return True
    
    return False
```

### 4.3 The Leak Action
**File: `engine.py`:**
```python
def leak_dm(self, player: Entity, target_npc_id: str, leaked_dm_text: str) -> Event:
    """
    Player leaks a fabricated DM from high-aura NPC.
    This triggers a CRUCIBLE for the target NPC, not player.
    Cost: 150 Aura
    """
    cost = 150
    if player.aura < cost:
        return None
    
    target = self.state.entities.get(target_npc_id)
    
    # Create synthetic DM leak event
    event = Event(
        id=str(uuid.uuid4()),
        type="dm_leak",
        timestamp=time.time(),
        protagonist_id=player.id,
        villain_id=target_npc_id,
        content_summary=f"LEAKED: DM from {target.name}: '{leaked_dm_text[:100]}'",
        impact={"triggers_crucible_for": target_npc_id}
    )
    
    # Trigger crucible for target, not player
    self.trigger_crucible(target)
    player.aura -= cost
    
    print(f"[LEAK] {player.name} leaked DM from {target.name}")
    return event
```

---

## 5️⃣ FRONTEND FEEDBACK JUICINESS

### 5.1 Stat Float Animations
**File: `src/components/StatFloat.tsx`** (NEW):
```typescript
export interface StatFloat {
  value: number;
  type: "aura" | "heat" | "wealth" | "followers";
  x: number;
  y: number;
  duration: number;
  isPositive: boolean;
}

export function StatFloatLayer() {
  const [floats, setFloats] = useState<StatFloat[]>([]);

  useEffect(() => {
    // Subscribe to stat change events
    window.addEventListener("stat-change", (e: CustomEvent) => {
      const newFloat = e.detail;
      setFloats(prev => [...prev, newFloat]);
      
      setTimeout(() => {
        setFloats(prev => prev.filter(f => f !== newFloat));
      }, newFloat.duration);
    });
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none">
      {floats.map(float => (
        <FloatAnimation key={float.value} float={float} />
      ))}
    </div>
  );
}

function FloatAnimation({ float }: { float: StatFloat }) {
  return (
    <div
      className="absolute font-bold text-sm animate-float"
      style={{
        left: float.x,
        top: float.y,
        color: float.isPositive ? "#4ade80" : "#f87171",
        animation: `floatUp ${float.duration}ms ease-out forwards`
      }}
    >
      {float.isPositive ? "+" : "-"}{Math.abs(float.value)} {float.type}
    </div>
  );
}
```

**CSS Animation:**
```css
@keyframes floatUp {
  0% {
    opacity: 1;
    transform: translateY(0);
  }
  100% {
    opacity: 0;
    transform: translateY(-60px);
  }
}
```

### 5.2 Sound Effects
**File: `src/utils/sounds.ts`** (NEW):
```typescript
export const SOUND_EFFECTS = {
  notification: "/sounds/ding.mp3",
  dogpile: "/sounds/glitch.mp3",
  crucible_start: "/sounds/hum.mp3",
  post_success: "/sounds/whoosh.mp3",
  verified_unlock: "/sounds/unlock.mp3",
  deplatform: "/sounds/error.mp3"
};

export function playSound(effect: keyof typeof SOUND_EFFECTS) {
  const audio = new Audio(SOUND_EFFECTS[effect]);
  audio.volume = 0.5;
  audio.play().catch(() => {}); // Silent fail if blocked
}
```

**Integration in components:**
```typescript
async function handlePost() {
  const result = await postTweet(content);
  if (result.success) {
    playSound("post_success");
    dispatchStatFloat("+10 Aura", "+highlight");
  }
}
```

---

## 📋 Implementation Checklist

### Phase 1: Account Lifecycle (3-4 hours)
- [ ] Add account tier fields to Entity model
- [ ] Implement deplatforming trigger logic
- [ ] Create new account flow (legacy bonus inheritance)
- [ ] Wire tier progression quest checks to gamification system
- [ ] Test: Player reaches verified tier, then gets deplatformed

### Phase 2: NPC Evolution (4-5 hours)
- [ ] Add job/career fields to Entity
- [ ] Implement daily career simulation loop
- [ ] Add relationship-based auto-reply generation
- [ ] Implement relationship decay over time
- [ ] Test: NPC changes job, loses followers; player posts → hater auto-replies

### Phase 3: World Events (3-4 hours)
- [ ] Implement Hater Winter event trigger
- [ ] Add algorithmic shift system with topic multipliers
- [ ] Enhance faction warfare to generate autonomous conflicts
- [ ] Create world event modifier system
- [ ] Test: Event triggers, affects NPC behavior

### Phase 4: God Mode (2-3 hours)
- [ ] Implement Propaganda Machine (buy NPC control)
- [ ] Add Edit Internal Truth (reveal & modify)
- [ ] Implement Leak DM action
- [ ] Wire to Shadow Market UI

### Phase 5: Feedback (1-2 hours)
- [ ] Create StatFloat component with animations
- [ ] Add sound effect system
- [ ] Wire sounds to key events
- [ ] Test: Post → float animation + sound

---

## 🚀 Getting Started

**Start with Phase 1 (Account Lifecycle)** because:
1. It creates urgency (deplatforming = game over)
2. It gates other features (tier unlocks reach)
3. Relatively isolated changes
4. High player-facing impact

**Then Phase 2 (NPC Evolution)** because:
1. Builds on Phase 1 persistence
2. Makes the world feel alive
3. Creates emergent narratives

**Then Phase 3 (World Events)** because:
1. Makes the simulation unpredictable
2. Creates story moments
3. Integrates all prior systems

See individual sections for specific code diffs.
