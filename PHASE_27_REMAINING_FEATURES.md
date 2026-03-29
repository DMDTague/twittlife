# Phase 27 BitLife Integration - Remaining Features Guide

## Part 2: World Events System (2-3 hours)

### Architecture Overview
The world needs to feel **alive and unpredictable**. Events should:
1. Affect ALL NPCs (global modifiers)
2. Create narrative moments (rich descriptions)
3. Be triggered randomly but on a schedule
4. Cascade into NPC behavior changes

### Implementation Plan

#### 2.1 World Events Data Structure
**Add to [models.py](models.py)**:
```python
class WorldEvent(BaseModel):
    id: str
    type: str  # "hater_winter", "algorithm_shift", "scandal", "boom", "crash"
    name: str
    description: str
    start_day: int
    end_day: int  # -1 for instant events
    modifiers: Dict[str, float]  # Effect multipliers
    affected_npcs: List[str] = Field(default_factory=list)
    is_active: bool = True

class GameState(BaseModel):
    # ... existing fields ...
    active_world_events: List[WorldEvent] = Field(default_factory=list)
    algorithmic_topic_multipliers: Dict[str, float] = Field(default_factory=dict)  # topic → reach
    next_event_day: int = 0  # When next event should trigger
```

#### 2.2 Hater Winter Event
**Add to [engine.py](engine.py)**:
```python
def trigger_hater_winter(self) -> WorldEvent:
    """
    All NPCs' hostility +50% for 7 days.
    Chance: 2% per day
    """
    if random.random() > 0.02:
        return None
    
    event = WorldEvent(
        id=str(uuid.uuid4()),
        type="hater_winter",
        name="❄️ HATER WINTER",
        description="A wave of hostility sweeps the timeline. Everyone's meaner.",
        start_day=self.current_day,
        end_day=self.current_day + 7,
        modifiers={"hostility_boost": 0.5, "heat_mult": 2.0}
    )
    
    # Boost all NPCs
    for npc in self.state.entities.values():
        if not npc.is_player:
            npc.trait_matrix.hostility = min(100, 
                int(npc.trait_matrix.hostility * 1.5))
    
    self.state.active_world_events.append(event)
    print(f"[WORLD] Hater Winter begins!")
    return event

def trigger_algorithmic_shift(self) -> WorldEvent:
    """
    Every 5 days, reach multipliers change dramatically.
    Some topics explode (10x), others die (0.1x).
    """
    topics = ["tech", "combat_sports", "politics", "gaming", "philly_local", "finance"]
    shifts = {topic: random.choice([0.1, 0.5, 1.0, 2.0, 5.0, 10.0]) for topic in topics}
    
    # Boost/kill 2-3 random topics
    for _ in range(random.randint(2, 3)):
        topic = random.choice(topics)
        shifts[topic] = random.choice([0.05, 10.0])  # Extreme shift
    
    event = WorldEvent(
        id=str(uuid.uuid4()),
        type="algorithm_shift",
        name="🔄 ALGORITHM SHIFTED",
        description=f"The algo changed. New winners: {', '.join([k for k,v in sorted(shifts.items(), key=lambda x: x[1], reverse=True)][:3])}",
        start_day=self.current_day,
        end_day=self.current_day + 5,
        modifiers=shifts
    )
    
    self.state.algorithmic_topic_multipliers = shifts
    self.state.active_world_events.append(event)
    print(f"[WORLD] Algorithm Shift: {shifts}")
    return event

def get_active_world_modifier(self, modifier_key: str) -> float:
    """
    Returns current world modifier (hostility, heat, etc).
    Stacks all active events.
    """
    base = 1.0
    for event in self.state.active_world_events:
        if event.is_active and self.current_day <= event.end_day:
            if modifier_key in event.modifiers:
                base *= event.modifiers[modifier_key]
    return base

def cleanup_expired_events(self):
    """
    Called daily. Remove events past end_day.
    """
    for event in self.state.active_world_events[:]:
        if self.current_day > event.end_day and event.end_day != -1:
            event.is_active = False
            self.state.active_world_events.remove(event)
            print(f"[WORLD] {event.name} ended")
```

#### 2.3 Integration Points

**In [engine.py](engine.py) - modify `process_action(event)`**:
```python
def process_action(self, event: Event):
    # ... existing code ...
    
    # Apply world modifiers to event impact
    if event.type == "tweet" and event.initiator_id != "SYSTEM":
        entity = self.state.entities.get(event.initiator_id)
        if entity:
            # Get topic reach multiplier
            topic = list(event.impact_vectors.keys())[0] if event.impact_vectors else "general"
            reach_mult = self.state.algorithmic_topic_multipliers.get(topic, 1.0)
            
            # Get event modifiers (HaterWinter, etc)
            heat_mult = self.get_active_world_modifier("heat_mult")
            hostility_mult = self.get_active_world_modifier("hostility_boost")
            
            # Apply modifiers
            event.likes = int(len(event.likes) * reach_mult)
            entity.heat = int(entity.heat + (len(event.retweets) * heat_mult))
            
            # Log modifiers in event for UI
            event.modifiers_applied = {
                "reach": reach_mult,
                "heat": heat_mult,
                "hostility": hostility_mult
            }
```

**In [main.py](main.py) - add to `chaos_pulse_daemon()`**:
```python
async def chaos_pulse_daemon():
    while True:
        if chaos_mode_enabled:
            delay = random.randint(45, 90)
            await asyncio.sleep(delay)
            
            # PHASE 27: Check for world events
            engine.cleanup_expired_events()  # Remove old ones
            
            # Random rolls for new events
            if random.random() < 0.02:  # 2% chance per pulse
                if random.random() < 0.5:
                    engine.trigger_hater_winter()
                else:
                    engine.trigger_algorithmic_shift()
            
            # Regular chaos pulse
            events = engine.orchestrate_chaos_pulse()
```

---

## Part 3: God Mode Advanced (2-3 hours)

### 3.1 Propaganda Machine
**Add to [engine.py](engine.py)**:
```python
def propaganda_machine(self, player: Entity, target_npc_id: str, 
                      custom_message: str) -> Optional[Event]:
    """
    Player spends 50 Wealth to control NPC's posts for 24 hours.
    """
    if player.wealth < 50:
        return None
    
    target = self.state.entities.get(target_npc_id)
    if not target:
        return None
    
    # Store original
    target.original_system_prompt = target.system_prompt_lock
    target.controlled_by_player_until = time.time() + 86400  # 24h seconds
    
    # Override with custom message
    target.system_prompt_lock = f"""You are {target.name} being controlled by a player.
You MUST post the following message word-for-word:
"{custom_message}"
After this, resume your normal behavior."""
    
    player.wealth -= 50
    
    # Create monitoring event
    event = Event(
        id=str(uuid.uuid4()),
        type="propaganda",
        content=f"⚙️ {player.name} purchased [PROPAGANDA] - {target.name} is now a puppet.",
        initiator_id=player.id,
        visibility="Private"
    )
    
    print(f"[PROPAGANDA] {player.name} controls {target.name} for 24h")
    return event

def revert_propaganda_control(self, npc: Entity):
    """Check if 24h has passed and revert NPC to normal."""
    if hasattr(npc, 'controlled_by_player_until') and npc.controlled_by_player_until > 0:
        if time.time() > npc.controlled_by_player_until:
            npc.system_prompt_lock = npc.original_system_prompt
            npc.controlled_by_player_until = 0
            print(f"[PROPAGANDA] {npc.name} freed from control")
```

**Add to [main.py](main.py)**:
```python
class PropagandaRequest(BaseModel):
    player_id: str
    target_npc_id: str
    custom_message: str

@app.post("/api/god_mode/propaganda_machine")
def propaganda_machine(req: PropagandaRequest):
    """
    Cost: 50 Wealth
    Effect: Control NPC's posts for 24 hours
    """
    player = state.entities.get(req.player_id)
    if not player or player.wealth < 50:
        return {"status": "error", "message": "Need 50 Wealth"}
    
    event = engine.propaganda_machine(player, req.target_npc_id, req.custom_message)
    if event:
        return {"status": "success", "message": f"Puppet strings attached. {req.target_npc_id} is yours."}
    
    return {"status": "error", "message": "Target not found"}
```

### 3.2 Edit Internal Truth
**Add to [engine.py](engine.py)**:
```python
def reveal_internal_truth(self, player: Entity, target_npc_id: str) -> dict:
    """
    Cost: 100 Aura
    Reveal NPC's system prompt + internal beliefs.
    """
    if player.aura < 100:
        return {"error": "Need 100 Aura", "cost": 100}
    
    target = self.state.entities.get(target_npc_id)
    if not target:
        return {"error": "NPC not found"}
    
    player.aura -= 100
    
    return {
        "status": "revealed",
        "system_prompt": target.system_prompt_lock[:150] + "...",
        "core_beliefs": target.long_term_memory.core_beliefs[:3],
        "grudges": target.long_term_memory.grudges[:3],
        "internal_truth": {k: v for k, v in list(target.internal_truth.items())[:10]},
        "hidden_relationships": target.long_term_memory.relationship_matrix
    }

def edit_internal_truth_word(self, player: Entity, target_npc_id: str, 
                           belief_key: str, old_word: str, new_word: str) -> bool:
    """
    Cost: 200 Aura
    Change one word in NPC's internal belief.
    E.g., "Phil's biggest fan" → "Phil's worst enemy"
    """
    if player.aura < 200:
        return False
    
    target = self.state.entities.get(target_npc_id)
    if not target or belief_key not in target.internal_truth:
        return False
    
    old_val = str(target.internal_truth[belief_key])
    if old_word not in old_val:
        return False  # Word not found
    
    new_val = old_val.replace(old_word, new_word, 1)
    target.internal_truth[belief_key] = new_val
    player.aura -= 200
    
    # Log the edit
    event = Event(
        id=str(uuid.uuid4()),
        type="truth_edit",
        content=f"✏️ {player.name} rewrote {target.name}'s truth: '{old_word}' → '{new_word}'",
        initiator_id=player.id,
        visibility="Private"
    )
    
    print(f"[EDIT TRUTH] Modified {target.name}: {old_word} → {new_word}")
    target.internal_truth_edit_count = getattr(target, 'internal_truth_edit_count', 0) + 1
    
    return True
```

**Add to [main.py](main.py)**:
```python
@app.post("/api/god_mode/reveal_truth")
def reveal_truth(player_id: str, target_npc_id: str):
    """Reveal NPC's system prompt + beliefs. Cost: 100 Aura"""
    player = state.entities.get(player_id)
    if not player:
        raise HTTPException(status_code=404)
    
    result = engine.reveal_internal_truth(player, target_npc_id)
    return result

class EditTruthRequest(BaseModel):
    player_id: str
    target_npc_id: str
    belief_key: str
    old_word: str
    new_word: str

@app.post("/api/god_mode/edit_truth")
def edit_truth(req: EditTruthRequest):
    """Rewrite one word in NPC's belief. Cost: 200 Aura"""
    player = state.entities.get(req.player_id)
    target = state.entities.get(req.target_npc_id)
    
    if not player or not target:
        raise HTTPException(status_code=404)
    
    success = engine.edit_internal_truth_word(
        player, req.target_npc_id, req.belief_key, 
        req.old_word, req.new_word
    )
    
    if success:
        return {"status": "success", "message": f"Truth rewritten: {req.old_word} → {req.new_word}"}
    
    return {"status": "error", "message": "Edit failed"}
```

### 3.3 Leak DM
**Add to [engine.py](engine.py)**:
```python
def leak_dm(self, player: Entity, target_npc_id: str, 
           leaked_dm_text: str) -> Optional[Event]:
    """
    Cost: 150 Aura
    Leak a fabricated DM from target.
    Triggers Crucible for TARGET NPC (not player).
    """
    if player.aura < 150:
        return None
    
    target = self.state.entities.get(target_npc_id)
    if not target:
        return None
    
    player.aura -= 150
    
    # Create public leak event
    leak_event = Event(
        id=str(uuid.uuid4()),
        type="dm_leak",
        content=f"🔓 LEAKED DM from {target.name}:\n\n'{leaked_dm_text}'",
        initiator_id="SYSTEM",
        visibility="Public",
        timestamp=time.time()
    )
    self.state.events.append(leak_event)
    
    # Crucible for target (not player)
    self.trigger_crucible(target, leak_event)
    target.crucible_failures += 1
    
    print(f"[LEAK] {player.name} leaked DM from {target.name}")
    return leak_event

def trigger_crucible(self, target: Entity, trigger_event: Optional[Event] = None):
    """
    Force target into a Crucible (crisis event).
    Target must respond or lose Aura.
    """
    if not trigger_event:
        trigger_event = self.state.events[-1] if self.state.events else None
    
    crucible_msg = f"""{target.name}, you're in a CRUCIBLE!
    
Leaked DM is spreading. You must respond within the hour or lose 1000 Aura.
Your reputation is on the line."""
    
    # Notify target (push to frontend)
    crucible_event = Event(
        id=str(uuid.uuid4()),
        type="crucible",
        content=crucible_msg,
        initiator_id="SYSTEM",
        target_ids=[target.id],
        visibility="Private",
        timestamp=time.time()
    )
    
    self.state.events.append(crucible_event)
    print(f"[CRUCIBLE] {target.name} triggered by leak!")
```

**Add to [main.py](main.py)**:
```python
class LeakDMRequest(BaseModel):
    player_id: str
    target_npc_id: str
    dm_text: str

@app.post("/api/god_mode/leak_dm")
def leak_dm(req: LeakDMRequest):
    """Leak fabricated DM. Cost: 150 Aura. Triggers Crucible for TARGET."""
    player = state.entities.get(req.player_id)
    target = state.entities.get(req.target_npc_id)
    
    if not player or not target:
        raise HTTPException(status_code=404)
    
    if player.aura < 150:
        return {"status": "error", "message": "Need 150 Aura"}
    
    event = engine.leak_dm(player, req.target_npc_id, req.dm_text)
    
    if event:
        return {
            "status": "success",
            "message": f"DM leaked. {target.name} is now in CRUCIBLE mode.",
            "leak_event_id": event.id
        }
    
    return {"status": "error", "message": "Leak failed"}
```

---

## Part 4: Frontend Feedback Juiciness (1-2 hours)

### 4.1 Stat Float Animations
**Create [src/components/StatFloat.tsx](twitlife/src/components/StatFloat.tsx)**:
```typescript
import React, { useState, useEffect } from 'react';
import './StatFloat.css';

export interface StatFloe {
  id: string;
  value: number;
  type: "aura" | "heat" | "wealth" | "followers";
  x: number;
  y: number;
  duration: number;
  isPositive: boolean;
}

export function useStatFloats() {
  const [floats, setFloats] = useState<StatFloat[]>([]);

  useEffect(() => {
    // Listen for post success + stat change events
    const handlePostSuccess = (e: CustomEvent) => {
      const { delta, type, x, y } = e.detail;
      const newFloat: StatFloat = {
        id: Math.random().toString(),
        value: Math.abs(delta),
        type,
        x,
        y,
        duration: 1500,
        isPositive: delta > 0
      };
      
      setFloats(prev => [...prev, newFloat]);
      
      // Remove after animation
      setTimeout(() => {
        setFloats(prev => prev.filter(f => f.id !== newFloat.id));
      }, 1500);
    };

    window.addEventListener('stat-float', handlePostSuccess as EventListener);
    return () => window.removeEventListener('stat-float', handlePostSuccess as EventListener);
  }, []);

  return floats;
}

export function StatFloatLayer() {
  const floats = useStatFloats();

  return (
    <div className="stat-float-layer">
      {floats.map(float => (
        <div
          key={float.id}
          className={`stat-float ${float.isPositive ? 'positive' : 'negative'}`}
          style={{
            left: `${float.x}px`,
            top: `${float.y}px`,
            '--duration': `${float.duration}ms`
          } as React.CSSProperties}
        >
          {float.isPositive ? '+' : '-'}{float.value} {float.type}
        </div>
      ))}
    </div>
  );
}
```

**Create [src/components/StatFloat.css](twitlife/src/components/StatFloat.css)**:
```css
.stat-float-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
}

.stat-float {
  position: absolute;
  font-weight: bold;
  font-size: 16px;
  user-select: none;
  animation: floatUp var(--duration, 1500ms) ease-out forwards;
}

.stat-float.positive {
  color: #4ade80; /* Green */
  text-shadow: 0 0 4px rgba(74, 222, 128, 0.5);
}

.stat-float.negative {
  color: #f87171; /* Red */
  text-shadow: 0 0 4px rgba(248, 113, 113, 0.5);
}

@keyframes floatUp {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateY(-60px) scale(0.8);
  }
}
```

### 4.2 Sound Effects
**Create [src/utils/sounds.ts](twitlife/src/utils/sounds.ts)**:
```typescript
// Public sounds should be in /public/sounds/
// Generate or place these files:
// - ding.mp3, glitch.mp3, hum.mp3, whoosh.mp3, error.mp3, unlock.mp3

const SOUND_EFFECTS = {
  notification: "/sounds/ding.mp3",        // When reply/like arrives
  dogpile: "/sounds/glitch.mp3",          // Started getting dogpiled
  crucible_start: "/sounds/hum.mp3",      // Crucible triggered
  post_success: "/sounds/whoosh.mp3",     // Post published
  verified_unlock: "/sounds/unlock.mp3",  // Tier up to verified
  deplatform: "/sounds/error.mp3",        // Account banned
  money: "/sounds/cash.mp3"               // Wealth earned
};

let volume = 0.5; // User-adjustable

export function setVolume(v: number) {
  volume = Math.max(0, Math.min(1, v));
}

export function playSound(effect: keyof typeof SOUND_EFFECTS) {
  try {
    const audio = new Audio(SOUND_EFFECTS[effect]);
    audio.volume = volume;
    audio.play();
  } catch (e) {
    // Silent fail - user may have blocked audio
    console.log(`Sound blocked: ${effect}`);
  }
}

export function playSequence(effects: (keyof typeof SOUND_EFFECTS)[], 
                            delayMs: number = 150) {
  effects.forEach((effect, i) => {
    setTimeout(() => playSound(effect), delayMs * i);
  });
}
```

### 4.3 Hook it Up
**In [src/pages/Feed.tsx](twitlife/src/pages/Feed.tsx)** (or wherever posts are created):
```typescript
import { playSound } from '@/utils/sounds';
import { StatFloatLayer } from '@/components/StatFloat';

export function FeedPage() {
  const handlePostSuccess = async (result) => {
    if (result.status === "success") {
      // Play sound
      playSound("post_success");
      
      // Emit stat float event
      window.dispatchEvent(new CustomEvent('stat-float', {
        detail: {
          delta: +10,  // Positive
          type: 'aura',
          x: window.innerWidth / 2,
          y: window.innerHeight / 2
        }
      }));
    }
    
    if (result.status === "deplatformed") {
      playSound("deplatform");
      // Show "Game Over" modal
    }
  };

  return (
    <>
      <StatFloatLayer />
      {/* Rest of feed */}
    </>
  );
}
```

---

## Summary: Total Implementation Time

| Feature | Time | Status |
|---------|------|--------|
| Account Lifecycle | ✅ 2h | Done |
| NPC Career Evolution | ✅ 1.5h | Done |
| Relationship Auto-Replies | ✅ 1.5h | Done |
| Tier Progression | ✅ 1h | Done |
| **World Events** | 🔄 3h | Ready |
| **God Mode Advanced** | 🔄 3h | Ready |
| **Frontend Juiciness** | 🔄 2h | Ready |
| **Testing & Polish** | 1-2h | Pending |
| **TOTAL** | **~20h** | 30% Complete |

---

## Quick Win Implementation Order

**If pressed for time, do in this order:**
1. ✅ Account Lifecycle (DONE - most impactful, creates urgency)
2. 🔄 Hater Winter event (3% of remaining time, huge impact)
3. 🔄 Propaganda Machine (1h, high fun factor)
4. 🔄 Stat float animations (1h, polish)

This gives 80% of the "BitLife feel" with 30% of the remaining work!
