import random
import json
import time
import os
import math
import uuid
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

from models import GameState, Event, Entity
from dictionaries import get_all_dict_keys
from fandom_math import FactionMath

load_dotenv()
try:
    groq_client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
    )
except Exception as e:
    groq_client = None
    print(f"Failed to initialize Groq client: {e}")


class GameEngine:
    def __init__(self, state: GameState):
        self.state = state
        self.current_day = 1 # Track in-game days
        self.active_pulse = None
        self.on_new_event = None # Stores {topic, protagonist_name, timestamp}
        
        # Phase 24: Strategy & Warfare
        self.simulation_era = "Peace" # Peace, Bloodbath, Purge
        self.era_modifers = {
            "Peace": {"heat_mult": 1.0, "audit_chance": 0.05},
            "Bloodbath": {"heat_mult": 0.5, "audit_chance": 0.02}, # Lower risk for bought growth
            "Purge": {"heat_mult": 2.0, "audit_chance": 0.50}      # High risk
        }
        
        # Phase 19: Performance Infrastructure
        from rate_limiter import rate_limiter, vibe_cache
        self.rate_limiter = rate_limiter
        self.vibe_cache = vibe_cache
        self.max_reactions_per_event = 5  # Configurable cap
        self.max_pulse_entities = 50     # Batched pulse processing cap
        
        # Phase 27: World Events System
        self.active_world_events = []
        self.algorithmic_topic_multipliers = {
            "tech": 1.0, "combat_sports": 1.0, "politics": 1.0,
            "gaming": 1.0, "philly_local": 1.0, "finance": 1.0
        }
        self.hater_winter_active = False
        self.hater_winter_end_day = 0
        
        # Phase 21.1: Community Notes Fallback
        self.community_notes_dataset = [
            "Readers added context: This claim is factually disputed by multiple sources.",
            "Readers added context: The image in this post is AI-generated and not a real photograph.",
            "Readers added context: This quote is taken completely out of context from a larger interview.",
            "Readers added context: Statistical data from 2026 shows the opposite trend.",
            "Readers added context: This is a known satirical account."
        ]
        import os
        if os.path.exists("community_notes.csv"):
            import pandas as pd
            try:
                df = pd.read_csv("community_notes.csv")
                self.community_notes_dataset = df["note_text"].tolist()
            except:
                pass


    def add_entity(self, entity: Entity):
        self.state.entities[entity.id] = entity
        
    def analyze_tweet_vibe(self, tweet_text: str) -> dict:
        """
        Uses Groq API to extract hidden 'impact_vectors' from a tweet text.
        Returns a dictionary of vibe categories and their -100 to 100 scores.
        Rate-limited via Phase 19 guardrails.
        """
        if not groq_client:
            return {}
        
        # Phase 19: Rate limit check
        can_go, reason = self.rate_limiter.can_proceed(estimated_tokens=400)
        if not can_go:
            print(f"[RATE LIMIT] analyze_tweet_vibe blocked: {reason}")
            return {}

        master_keys = get_all_dict_keys()
        
        prompt = f'''
You are an advanced social sentiment analyzer. Read the following tweet and extract its hidden social, ideological, or lifestyle metadata.
Identify the top 1 to 4 most relevant "vibe" categories FROM THE SPECIFIC LIST BELOW.
You MUST ONLY use exact keys from this list. Do not invent your own.
Assign a score from -100 to 100 for each, representing where the tweet falls on that scale.

Master Key List:
{master_keys}

Ensure you output a valid JSON object with EXACTLY this structure:
{{
  "impact_vectors": {{
    "exact_key_from_list": score,
    ...
  }}
}}

Tweet: "{tweet_text}"
'''
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=200,
                temperature=0.3
            )
            data = json.loads(response.choices[0].message.content.strip())
            vectors = data.get("impact_vectors", {})
            # Phase 19: Record token usage
            tokens_used = getattr(response.usage, 'total_tokens', 400) if hasattr(response, 'usage') else 400
            self.rate_limiter.record_usage(tokens_used)
            return vectors
        except Exception as e:
            print(f"[ENGINE] Vibe Analysis Failed: {e}")
            return {}

    def process_action(self, event: Event):
        """
        Processes an action, updates the game state, and modifies short/long term memory.
        """
        self.state.events.append(event)
        
        if self.on_new_event:
            self.on_new_event(event)

    def trait_drift(self, entity: Entity, impact_vectors: dict):
        """
        Phase 22: Slowly pull the entity's internal_truth toward the public_vibe
        if they keep posting outside their original character.
        """
        for category, p_score in impact_vectors.items():
            true_vibe = entity.internal_truth.get(category, 0.0)
            drift = (p_score - true_vibe) * 0.10
            entity.internal_truth[category] = true_vibe + drift
            
    def trigger_life_event(self, entity: Entity, milestone_count: int):
        import uuid
        milestone_text = "invited to a Main Line influencer party" if milestone_count == 5000 else "recognized by SEPTA Karens in public" if milestone_count == 10000 else "approached by a shady PAC for endorsements"
        event = Event(
            id=str(uuid.uuid4()),
            type="dm",
            content=f"🎉 LIFE EVENT: You reached {milestone_count} followers! You've been {milestone_text}. Your influence is spilling into the real world.",
            initiator_id="SYSTEM",
            visibility="Private",
            target_ids=[entity.id]
        )
        self.state.events.append(event)
        if self.on_new_event:
            self.on_new_event(event)

    def evaluate_crisis_response(self, player: Entity, event_description: str, player_response: str, risk_multiplier: float):
        """Phase 23: The LLM judges the player's PR response to a major event."""
        if not groq_client:
            return {"verdict": "Algorithm offline.", "aura_change": 0, "follower_change": 0}

        prompt = f"""
        You are the omniscient algorithm of a toxic social media network.
        The player faced this massive public event: "{event_description}"
        
        The player responded with this public post: "{player_response}"
        
        Evaluate their response. Did they apologize well? Did they double down and look like a badass to their base? Or did they look weak and get ratio'd?
        
        Output STRICT JSON:
        {{
            "verdict_text": "A 1-sentence description of the crowd's reaction (e.g., 'Your fake apology was torn apart by the swarm.')",
            "aura_change": [integer between -500 and +500],
            "follower_change": [integer between -5000 and +5000]
        }}
        """

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=200,
                temperature=0.7
            )
            data = json.loads(response.choices[0].message.content.strip())
            
            # Apply mathematical damage/buff
            final_aura_change = int(data.get("aura_change", 0) * risk_multiplier)
            final_follower_change = int(data.get("follower_change", 0) * risk_multiplier)
            
            player.aura = getattr(player, 'aura', 0) + final_aura_change
            player.follower_count += final_follower_change
            
            return {
                "verdict": data.get("verdict_text", "The swarm is indifferent."),
                "aura_change": final_aura_change,
                "follower_change": final_follower_change
            }
        except Exception as e:
            print(f"[ENGINE] Crisis Evaluation Failed: {e}")
            return {"verdict": "The algorithm glitched out.", "aura_change": 0, "follower_change": 0}

    def update_alliance_score(self, player: Entity, titan_id: str, message: str):
        """Phase 23: Update hidden alliance score with Titans in DMs."""
        alliance_scores = getattr(player, 'alliance_scores', {})
        current_score = alliance_scores.get(titan_id, 0)
        
        # Pull Titan personality traits
        titan = self.state.entities.get(titan_id)
        if not titan: return
        
        # Simple heuristic: positive keywords increase affinity
        positives = ["agree", "solid", "true", "legend", "goat", "based"]
        negatives = ["wrong", "bad", "stupid", "lame", "cringe"]
        
        delta = 0
        for w in positives:
            if w in message.lower(): delta += 5
        for w in negatives:
            if w in message.lower(): delta -= 5
            
        alliance_scores[titan_id] = max(0, min(100, current_score + delta))
        player.alliance_scores = alliance_scores
        print(f"[ALLIANCE] {player.name} score with {titan_id}: {player.alliance_scores[titan_id]}")

    # ==========================================
    # MEMORY & SOCIAL DYNAMICS
    
        # Apply the mathematically driven Vibe Shift if the event has impact vectors.
        # This solidifies the "Public Vibe" perception of the initiator.
        initiator = self.state.entities.get(event.initiator_id)
        if initiator and event.impact_vectors:
            alpha = 0.2 # Sensitivity Constant (how much 1 tweet shifts perception)
            # Certainty Factor (C): A crude approximation based on follower count.
            # Max C = 1.0 (easy to move), Min C = 0.1 (hard to move for massive accounts)
            c_factor = max(0.1, 1.0 - (initiator.follower_count / 100000.0)) 
            
            for category, p_score in event.impact_vectors.items():
                current_vibe = initiator.public_vibe.get(category, 0.0)
                # ΔV = α * (P - V) * C
                delta_v = alpha * (p_score - current_vibe) * c_factor
                initiator.public_vibe[category] = current_vibe + delta_v
                print(f"[VIBE SHIFT] {initiator.name} - {category}: {current_vibe:.1f} -> {initiator.public_vibe[category]:.1f} (P={p_score})")

            # Phase 24.4: Domain Alignment & Toxicity Recovery
            tone = event.impact_vectors.get("tone", 0.0)
            hostility = event.impact_vectors.get("hostility", 0.0)
            if tone > 30 and hostility < 0:
                initiator.toxicity_fatigue = max(0, initiator.toxicity_fatigue - 2)
                print(f"[RECOVERY] @{initiator.id} reduced Toxicity Fatigue to {initiator.toxicity_fatigue} via non-toxic post.")

            # Phase 22: Protagonist Depth (Trait Drift & Life Events)
            # Update aura_peak
            if initiator.aura > initiator.aura_peak:
                initiator.aura_peak = initiator.aura
                
            # Check 5k follower milestone for Life Events
            target_milestone = (initiator.follower_count // 5000) * 5000
            current_milestone = initiator.internal_truth.get('_last_milestone', 0)
            if target_milestone > current_milestone and target_milestone > 1000:
                initiator.internal_truth['_last_milestone'] = target_milestone
                self.trigger_life_event(initiator, int(target_milestone))

        # Phase 24.1: Decrement Aura Debt for the initiator
        if initiator and initiator.aura_debt_posts > 0:
            initiator.aura_debt_posts -= 1
            print(f"[AURA DEBT] @{initiator.id} debt remaining: {initiator.aura_debt_posts}")

            # Calculate Max Friction for Faction Wars & Community Notes
            max_friction = max([abs(s) for s in event.impact_vectors.values()] + [0])
            
            if abs(max_friction) > 70:
                self.force_quote_chain(event.id, max_friction)
                
            if abs(max_friction) > 60 and random.random() < 0.40:  # 40% chance on big fights
                note = random.choice(self.community_notes_dataset)
                import uuid
                note_event = Event(
                    id=str(uuid.uuid4()),
                    type="community_note",
                    content=f"Community Notes: {note}",
                    initiator_id="SYSTEM",
                    visibility="Public",
                    reply_to_id=event.id
                )
                self.state.events.append(note_event)
                print(f"[COMMUNITY NOTE] Added to post {event.id}")

            # Check for Mob Rule / Cancel Culture
            # If Aura drops too low and the post is highly polarizing, they get cancelled.
            import time
            if initiator.follower_count < 950: # Threshold for testing
                if not initiator.is_dogpiled or time.time() > initiator.dogpile_end_time:
                    is_polarizing = any(abs(score) > 75 for score in event.impact_vectors.values())
                    if is_polarizing or initiator.follower_count < 500:
                        self.trigger_targeted_dogpile(initiator, event)

        # Determine who should be impacted by this event based on visibility
        # Limit to a subset of online NPCs to avoid Groq Rate Limits (429)
        import random
        online_entities = [e for e in self.state.entities.values() if not e.is_player]
        random.shuffle(online_entities)
        
        # We cap reactions to simulate "The Swarm" without blowing API limits
        reaction_count = 0
        max_entities = min(self.max_reactions_per_event, len(online_entities))
        
        # Real-time reaction pipeline (lightweight)
        for entity in online_entities:
            if reaction_count >= max_entities:
                break
                
            if entity.id == event.initiator_id:
                self._update_memory(entity, event)
            else:
                visible_events = self.filter_events_for_entity(entity.id, [event])
                if visible_events:
                    self._update_memory(entity, event)
                    reaction_count += 1

    def _update_memory(self, entity: Entity, event: Event):
        """
        Simple heuristic logic to update memory based on the event.
        In a full game, this would be more complex and potentially involve an LLM call to evaluate sentiment.
        """
        entity.short_term_memory.recent_interactions.append(event.id)
        
        # Extremely basic relationship update (placeholder for LLM extraction)
        if event.initiator_id != entity.id and event.initiator_id in self.state.entities:
            current_score = entity.long_term_memory.relationship_matrix.get(event.initiator_id, 0)
            
            # Simulated naive relationship adjustment
            if "likes" in event.content.lower() or "nice" in event.content.lower() or "love" in event.content.lower():
                entity.long_term_memory.relationship_matrix[event.initiator_id] = min(100, current_score + 5)
                entity.short_term_memory.current_mood = "Happy"
            elif "hate" in event.content.lower() or "dumb" in event.content.lower() or "stupid" in event.content.lower():
                entity.long_term_memory.relationship_matrix[event.initiator_id] = max(-100, current_score - 10)
                entity.short_term_memory.current_mood = "Angry"

    # --- Phase 18: Narrative Evolution ---

    def track_ratio_and_grudge(self, winner_id: str, loser_id: str):
        """
        Called when 'winner' gets significantly more engagement than 'loser' on a clash.
        After 5 ratios, the loser develops a permanent Grudge.
        """
        loser = self.state.entities.get(loser_id)
        if not loser:
            return
        
        count = loser.ratio_tracker.get(winner_id, 0) + 1
        loser.ratio_tracker[winner_id] = count
        
        if count >= 5 and winner_id not in loser.long_term_memory.grudges:
            loser.long_term_memory.grudges.append(winner_id)
            print(f"[GRUDGE] {loser.name} now holds a PERMANENT GRUDGE against {winner_id} after being ratioed {count} times!")

    def apply_trait_drift(self, entity: Entity, exposure_vectors: dict):
        """
        Radicalization: If an NPC is exposed to high-velocity opposing posts,
        their internal truth slowly drifts ±5 points toward that direction.
        20% chance per exposure to trigger drift.
        """
        import random
        if random.random() > 0.20:  # Only 20% chance to drift
            return
        
        for trait, score in exposure_vectors.items():
            current = entity.internal_truth.get(trait, 0)
            # Only drift if the exposure is strongly opposed (score vs current on opposite sides)
            if abs(score) > 50 and ((score > 0 and current < 0) or (score < 0 and current > 0)):
                drift = 5 if score > 0 else -5
                new_val = max(-100, min(100, current + drift))
                entity.internal_truth[trait] = new_val
                print(f"[TRAIT DRIFT] {entity.name}: {trait} drifted {current} -> {new_val} (exposure: {score})")

    def check_rising_star_promotion(self, entity: Entity):
        """
        Rising Stars gain followers and archetype upgrades based on total engagement.
        """
        if not entity.is_rising_star:
            return
        
        if entity.total_engagement >= 50 and entity.archetype == "The Swarm":
            entity.archetype = "Micro-Celebrity"
            entity.follower_count += 2000
            entity.is_verified = True
            print(f"[RISING STAR] {entity.name} has been promoted to Micro-Celebrity! Followers: {entity.follower_count}")
        elif entity.total_engagement >= 100 and entity.archetype == "Micro-Celebrity":
            entity.archetype = "Local Legend"
            entity.follower_count += 5000
            if "Celebrity" not in entity.faction_tags:
                entity.faction_tags.append("Celebrity")
            print(f"[RISING STAR] {entity.name} ascended to Local Legend! Followers: {entity.follower_count}")

    def get_ranked_timeline(self, entity_id: str, limit: int = 50) -> list:
        """
        Returns a timeline sorted algorithmically by velocity (Likes/RTs over time) instead of purely chronologically.
        """
        import time
        current_time = time.time()
        
        visible_events = self.filter_events_for_entity(entity_id, self.state.events)
        
        ranked_events = []
        for ev in visible_events:
            # Time passed in "hours" (or minutes depending on simulation speed) 
            # Using seconds for testing to see immediate sorting changes
            time_passed = max(1.0, current_time - ev.timestamp)
            
            # Base logic: Velocity = Engagement / Time
            engagement_score = (len(ev.likes) * 2) + (len(ev.retweets) * 5)
            
            # Algorithm decay (Newer posts get an inherent boost)
            algorithmic_score = (engagement_score / time_passed) + (1000 / time_passed)
            
            # Bonus: Hacked/News events always float higher initially
            if ev.type in ["news", "hacked_tweet"]:
                algorithmic_score += 500
                
            # Bonus: Celebrities get an inherent algorithm boost
            initiator = self.state.entities.get(ev.initiator_id)
            if initiator and "Celebrity" in initiator.faction_tags:
                algorithmic_score += 100
                
            # Phase 16: Verification Algorithm
            if initiator and initiator.is_verified:
                algorithmic_score *= 2.5
                
            # Phase 24.1: Aura Debt Invisibility
            if initiator and initiator.aura_debt_posts > 0:
                algorithmic_score *= 0.01

            ranked_events.append({"event": ev, "score": algorithmic_score})
            
        # Sort by the highest algorithmic score
        ranked_events.sort(key=lambda x: x["score"], reverse=True)
        
        # Return the actual Event objects limit
        compiled_timeline = [item["event"] for item in ranked_events]
        final_feed = compiled_timeline[:limit]
        
        # Phase 16: Simulated Ad Targeting
        # Inject an ad every 10 posts based on the player's primary vectors
        if len(final_feed) >= 10:
            target_entity = self.state.entities.get(entity_id)
            if target_entity:
                ad_content = self._generate_simulated_ad(target_entity)
                if ad_content:
                    import uuid
                    ad_event = Event(
                        id=str(uuid.uuid4()),
                        type="ad",
                        content=ad_content,
                        initiator_id="SYSTEM",
                        visibility="Public"
                    )
                    # Insert the ad at rank 3
                    final_feed.insert(2, ad_event)

        return final_feed

    def filter_events_for_entity(self, entity_id: str, events: list) -> list:
        """
        Visibility algorithm replacing the simple filter.
        Tier 1 (Local): Seen by immediate NPCs (Swarm).
        Tier 2 (Trending): Seen by mid-tier (Swarm + Local Legends).
        Tier 3 (Viral): Seen by Celebrities.
        """
        import random
        viewer = self.state.entities.get(entity_id)
        if not viewer: return []
        
        visible = []
        for ev in events:
            if ev.initiator_id == entity_id:
                visible.append(ev)
                continue
            if ev.visibility == "Private" and entity_id not in ev.target_ids:
                continue
                
            initiator = self.state.entities.get(ev.initiator_id)
            if not initiator: continue

            # Phase 24.1: Aura Debt (99% Invisibility)
            if initiator.aura_debt_posts > 0 and random.random() > 0.01:
                continue

            # Determine algorithmic velocity/tier of the post
            engagement = len(ev.likes) + len(ev.retweets) * 2 + ev.replies_count * 3
            is_viral = engagement > 100
            is_trending = engagement > 20
            
            # Celebrities rarely see non-viral normal user posts, unless they are verifying or famous
            if "Celebrity" in viewer.faction_tags and not initiator.is_verified and initiator.follower_count < 5000:
                if not is_viral and random.random() > 0.005:  # 0.5% chance
                    continue
            
            # Non-Verified Normal Players should be heavily visible to Swarm Bots to simulate the algorithmic grind
            if viewer.agent_tier == "Basic" and not initiator.is_verified:
                # 80% natural visibility for the swarm to see local player posts
                if random.random() > 0.80 and engagement < 5:
                    continue
                    
            visible.append(ev)
            
        return visible

    def advance_day(self):
        """
        Advances the simulation by 1 in-game day.
        Triggers massive background calculations, world events, and autonomous posts.
        """
        import time
        import random
        self.current_day += 1
        print(f"[ENGINE] === ADVANCING TO DAY {self.current_day} ===")
        
        from economy import calculate_niche_income, process_supporter_conversion
        era_data = self.era_modifers.get(self.simulation_era, self.era_modifers["Peace"])
        for entity in self.state.entities.values():
            # Phase 27: Supporter Conversion
            if entity.last_known_follower_count == 0:
                entity.last_known_follower_count = entity.follower_count
            
            delta = entity.follower_count - entity.last_known_follower_count
            if delta > 0:
                process_supporter_conversion(entity, delta)
                entity.last_known_follower_count = entity.follower_count
            
            # Phase 26/27: Calculate Income Breakdown
            income_breakdown = calculate_niche_income(entity)
            entity.monthly_income_breakdown = income_breakdown
            
            # Phase 27: 30-Day Payday Logic
            if self.current_day - entity.last_payday_day >= 30:
                entity.wealth += income_breakdown["monthly_total"]
                entity.last_payday_day = self.current_day
                print(f"[ECONOMY] Payday for @{entity.id}! Total: {income_breakdown['monthly_total']}")
            
            if entity.heat > 0:
                entity.heat = max(0, entity.heat - 5)
            
            # Phase 24: Decay recent synthetic growth so old bots don't haunt forever
            if getattr(entity, 'recent_synthetic_growth', 0) > 0:
                entity.recent_synthetic_growth = int(entity.recent_synthetic_growth * 0.9)
            
            # Phase 24: Sigmoid Audit Engine
            # P_audit(H) = 1 / (1 + exp(-k * (H - H_crit)))
            H_crit = 75
            k = 0.2
            audit_prob = 1.0 / (1.0 + math.exp(-k * (entity.heat - H_crit)))
            
            if random.random() < (audit_prob * era_data["audit_chance"]):
                self.run_algorithmic_audit(entity)
            
            # Phase 24.1: Decay Toxicity Fatigue
            if entity.toxicity_fatigue > 0:
                entity.toxicity_fatigue = max(0, entity.toxicity_fatigue - 1)
            
            # Phase 24.1: Decay Buffs/Debt
                entity.momentum_buff_days -= 1
                
            # Phase 24.4: Griefing Account Detection & Aura Ceiling
            if entity.toxicity_fatigue > 7:
                if not entity.is_griefing_account:
                    entity.is_griefing_account = True
                    print(f"[SWARM] @{entity.id} has been labeled a 'Griefing Account'. Aura capped.")
            
            if entity.is_griefing_account:
                # Permanently cap Aura ceiling (e.g. 50k followers)
                entity.follower_count = min(entity.follower_count, 50000)
                entity.aura = min(entity.aura, 10000)
                
            # Reset shadowban if expired
            if entity.is_shadowbanned and time.time() > entity.shadowban_until:
                entity.is_shadowbanned = False

        # 2. Rotate Era every 7 days
        if self.current_day % 7 == 0:
            self.simulation_era = random.choice(["Peace", "Bloodbath", "Purge"])

        # 3. Fire a World Event (Trending news)
        self.trigger_global_event_injector()
        
        # 4. Phase 24: Nash Equilibrium Simulation (Faction Warfare)
        self.orchestrate_faction_warfare()
        
        # 5. Phase 24.1: Aura Tribunal (Judge active beefs)
        self.judge_active_beefs()
        
        # 6. Run background simulation tick (NPCs acting autonomously)
        self.background_simulation_tick()
        
        return {
            "day": self.current_day,
            "status": f"Advanced success. World pulse applied. Era: {self.simulation_era}",
            "simulation_era": self.simulation_era
        }

    def orchestrate_faction_warfare(self):
        """
        Phase 24: Deep Faction Warfare (Nash Equilibrium)
        Top 50 entities steal followers from rivals via smear campaigns.
        """
        import random
        sorted_entities = sorted(
            [e for e in self.state.entities.values() if not e.is_shadowbanned],
            key=lambda x: x.follower_count,
            reverse=True
        )[:50]
        
        for i, hunter in enumerate(sorted_entities):
            if hunter.is_player:
                continue
                
            targets = []
            if i > 0: targets.append(sorted_entities[i-1]) 
            if i < len(sorted_entities) - 1: targets.append(sorted_entities[i+1]) 
            
            for target in targets:
                # Phase 24.1: Use Domain Similarity for targeting
                vec_h = FactionMath.get_trait_vector(hunter.internal_truth)
                vec_t = FactionMath.get_trait_vector(target.internal_truth)
                similarity = FactionMath.calculate_domain_similarity(vec_h, vec_t)
                
                # Proximity check (5%)
                diff_pct = abs(hunter.follower_count - target.follower_count) / max(1, target.follower_count)
                
                if diff_pct < 0.05:
                    aggression = hunter.trait_matrix.hostility
                    
                    # If similarity is -1 (opposites), hostility is much higher
                    # If similarity is 1 (competitors), hostility is also high due to "Stan" friction
                    effective_aggression = aggression
                    if similarity < -0.5: effective_aggression += 30 # Opposites want war
                    if similarity > 0.8: effective_aggression += 20  # Competitors want to eliminate each other
                    
                    same_faction = any(tag in target.faction_tags for tag in hunter.faction_tags)
                    same_niche = hunter.primary_niche == target.primary_niche
                    
                    threshold = 50 if same_faction else 10
                    # Phase 24.3: Sovereignty Check - Same-niche aggression is 25% higher (lower threshold)
                    if same_niche:
                        threshold -= 15
                    
                    if random.randint(-100, 100) < (effective_aggression - threshold):
                        # Trigger Beef
                        self.initiate_beef(hunter, target)

    def initiate_beef(self, initiator: Entity, target: Entity):
        """Phase 24.1: Start a public feud between two entities."""
        if target.id in initiator.active_beefs:
            return
            
        initiator.active_beefs.append(target.id)
        target.active_beefs.append(initiator.id)
        
        # Increase Toxicity Fatigue for the aggressor
        initiator.toxicity_fatigue += 1
        
        # Apply immediate follower migration
        self.orchestrate_follower_migration(initiator, target)
        
        print(f"🔥 BEEF: @{initiator.id} has initiated a public feud with @{target.id}! Toxicity Fatigue: {initiator.toxicity_fatigue}")

    def orchestrate_follower_migration(self, a: Entity, b: Entity):
        """
        Calculates migration for Entity A (initiator) during a beef with Entity B.
        Uses FactionMath.calculate_follower_migration.
        """
        import random
        # 1. Calculate Stan Shield for B
        b_stans = FactionMath.calculate_stan_shield(b.follower_count, b.aura, b.aura_peak, b.phi_fanaticism)
        b_haters = b.hater_count or (b.follower_count // 10) # Fallback if hater_count not tracked well
        
        # 2. Viral Drama Multiplier
        # Assume 10% overlap and toxicity = toxicity_fatigue * 0.5
        shared = int(min(a.follower_count, b.follower_count) * 0.1)
        tau = min(2.0, a.toxicity_fatigue * 0.5)
        i_beef = FactionMath.calculate_viral_drama_multiplier(a.follower_count, b.follower_count, shared, tau)
        
        # Phase 24.3: The Grifter Penalty - Cross-Niche Chaos Bonus
        if a.primary_niche != b.primary_niche:
            i_beef *= 2.0
            print(f"[GRIFTER] Cross-niche beef detected. Chaos multiplier doubled to {i_beef}")
        
        # 3. Follower Migration for A
        # ρ: % of B's haters absorbed (0.05 to 0.1)
        # ω: % of new watchers converted (0.01 to 0.05) - drops with fatigue
        # σ: % of own moderates lost
        rho = 0.08
        omega_base = 0.03
        omega_actual = max(0.0, omega_base * (1.0 - (a.toxicity_fatigue / 10.0)))
        
        sigma_base = 0.02
        sigma_actual = FactionMath.calculate_toxicity_fatigue(sigma_base, a.toxicity_fatigue)
        
        delta_f_a = FactionMath.calculate_follower_migration(
            b_haters, i_beef, a.neutral_count or (a.follower_count // 2),
            rho, omega_actual, sigma_actual
        )
        
        # Apply change
        a.follower_count = max(10, a.follower_count + delta_f_a)
        
        # Update Stan/Neutral/Hater splits (crude redistribution)
        # B loses many neutrals but stays with stans
        migration_b = int(b.follower_count * 0.05)
        b.follower_count = max(b_stans, b.follower_count - migration_b)
        
        print(f"📉 MIGRATION: Beef results in @{a.id} ΔF: {delta_f_a:,}. @{b.id} shield held {b_stans:,} stans.")

    def judge_active_beefs(self):
        """
        Phase 24.1: The Aura Tribunal.
        Evaluates active beefs, determines winners/losers based on engagement.
        """
        processed_pairs = set()
        for entity in self.state.entities.values():
            for target_id in list(entity.active_beefs):
                pair = tuple(sorted([entity.id, target_id]))
                if pair in processed_pairs:
                    continue
                
                target = self.state.entities.get(target_id)
                if not target:
                    continue
                
                # Judge this beef
                self.apply_beef_consequences(entity, target)
                processed_pairs.add(pair)
                
                # Clear beef after judging (24h cycle)
                entity.active_beefs.remove(target_id)
                if entity.id in target.active_beefs:
                    target.active_beefs.remove(entity.id)

    def apply_beef_consequences(self, a: Entity, b: Entity):
        """
        Calculates Net Conflict Score (C) for both and delivers rewards/burns.
        """
        # Heuristic: Winner of the beef is determined by who has higher total_engagement 
        # relative to their size in the last 24h.
        score_a = FactionMath.calculate_net_conflict_score(
            likes=len([e for e in self.state.events if e.initiator_id == a.id and e.timestamp > (time.time() - 86400)]),
            quote_tweets=random.randint(5, 50), # Placeholder for real QT tracking
            ratios=random.randint(0, 5)        # Placeholder
        )
        score_b = FactionMath.calculate_net_conflict_score(
            likes=len([e for e in self.state.events if e.initiator_id == b.id and e.timestamp > (time.time() - 86400)]),
            quote_tweets=random.randint(5, 50),
            ratios=random.randint(0, 10)
        )
        
        winner, loser = (a, b) if score_a > score_b else (b, a)
        
        # Phase 24.3: The Grifter Penalty
        is_cross_niche = a.primary_niche != b.primary_niche
        penalty_multiplier = 2.0 if is_cross_niche else 1.0
        
        # Winner's Spoils: Momentum Buff (3 days)
        winner.momentum_buff_days = 3
        # Loser's Penalty: Neutral collapse & Aura Debt
        migration = int(loser.neutral_count * 0.2 * penalty_multiplier)
        loser.follower_count -= migration
        loser.neutral_count -= migration
        loser.aura_debt_posts = int(5 * penalty_multiplier)
        
        if is_cross_niche:
            print(f"[GRIFTER] Loser @{loser.id} hit with 2x penalty for cross-niche failure.")
        
        print(f"⚖️ TRIBUNAL: @{winner.id} WINS beef against @{loser.id}. Winner: Momentum Buff. Loser: Audience Collapse.")

    def run_algorithmic_audit(self, entity: Entity):
        """Phase 24: Penalize entities for high heat using the Deep Calculus of Clout."""
        import random
        import time
        
        # The Punishment: Wipe 1.5x the amount of synthetic followers recently bought
        purged_bots = int(entity.recent_synthetic_growth * 1.5)
        entity.follower_count = max(0, entity.follower_count - purged_bots)
        entity.recent_synthetic_growth = 0 # Reset after audit
        
        # Roll for secondary penalty
        penalty_type = random.choice(["shadowban", "aura_bankruptcy", "none"])
        
        if penalty_type == "shadowban":
            entity.is_shadowbanned = True
            entity.shadowban_until = time.time() + (3 * 86400) # 3 days
            print(f"🚩 AUDIT [SHADOWBAN]: @{entity.id} suspicious activity. Shadowbanned for 72h.")
        elif penalty_type == "aura_bankruptcy":
            entity.aura = int(entity.aura * 0.5)
            print(f"🚩 AUDIT [AURA BLOW]: Botting detected. @{entity.id} reputation destroyed.")
        
        print(f"🚩 AUDIT [PURGE]: Removed {purged_bots} illegitimate followers from @{entity.id}.")
        
        if entity.is_player:
            alert_msg = f"🚩 ALGORITHMIC AUDIT: {purged_bots} bots purged. "
            if penalty_type == "shadowban": alert_msg += "You are shadowbanned for 72h."
            elif penalty_type == "aura_bankruptcy": alert_msg += "Your reputation has collapsed."
            
            alert = Event(
                id=str(uuid.uuid4()),
                type="dm",
                content=alert_msg,
                initiator_id="SYSTEM",
                visibility="Private",
                target_ids=[entity.id]
            )
            self.state.events.append(alert)
            if self.on_new_event:
                self.on_new_event(alert)
        
    def background_simulation_tick(self):
        """
        Simulates hours of social media activity instantly.
        Picks random NPCs to post original content and others to react.
        """
        import random
        # Clear cache so new trending topics rotate in
        self.vibe_cache.clear()
        
        npcs = [e for e in self.state.entities.values() if not e.is_player]
        if not npcs: return
        
        # 1. Select 5-10 Active Posters
        num_posters = random.randint(5, 10)
        active_posters = random.sample(npcs, min(num_posters, len(npcs)))
        
        trending = self.get_trending_topics()
        topic = trending[0]['trait'].replace('_', ' ') if trending else "the timeline"
        
        for poster in active_posters:
            
            # Celebrity Beef / Discourse Logic (15% chance if poster is a Celebrity)
            if "Celebrity" in poster.faction_tags and random.random() < 0.15:
                other_celebs = [c for c in npcs if "Celebrity" in c.faction_tags and c.id != poster.id]
                if other_celebs:
                    target_celeb = random.choice(other_celebs)
                    # Find a conflicting trait to argue about
                    for trait, score in poster.internal_truth.items():
                        if abs(score) > 50 and target_celeb.internal_truth.get(trait, 0) * score < 0: # Opposite sides
                            beef_topic = f"Starting controversy with @{target_celeb.name} over {trait.replace('_', ' ')}"
                            event = self.generate_autonomous_post(poster, beef_topic)
                            if event:
                                event.content = f"@{target_celeb.id} {event.content}" # Directly tag them
                                self.process_action(event)
                                self.active_pulse = {
                                    "topic": f"CELEBRITY BEEF: {poster.name} vs {target_celeb.name}", 
                                    "protagonist": poster.name,
                                    "timestamp": time.time()
                                }
                                break
            else:
                event = self.generate_autonomous_post(poster, topic)
                if event:
                    self.process_action(event)
                
                # 2. Assign 2-5 random replies/likes from other NPCs to jumpstart velocity
                num_reactors = random.randint(2, 5)
                reactors = random.sample([n for n in npcs if n.id != poster.id], min(num_reactors, len(npcs)-1))
                for r in reactors:
                    if random.random() < 0.5:
                        event.likes.append(r.id)
                    elif random.random() < 0.2:
                        event.retweets.append(r.id)
                    elif random.random() < 0.3:
                        reply = self.generate_npc_reaction(r.id, event)
                        if reply:
                            self.process_action(reply)
                            
        print(f"[SIMULATION] Background tick complete. {num_posters} new threads created and populated.")

    def _generate_simulated_ad(self, target_entity: Entity) -> Optional[str]:
        """
        Calculates the Player's vector alignments and serves a targeted advertisement.
        """
        import random
        # Find extreme traits
        traits = target_entity.trait_matrix
        extreme_internal = sorted(target_entity.internal_truth.items(), key=lambda x: abs(x[1]), reverse=True)
        
        if not extreme_internal:
            return "PROMOTED: Protect your Digital Privacy with NorthVPN today."
            
        top_trait = extreme_internal[0][0]
        score = extreme_internal[0][1]
        
        # Primitive ad-server routing based on trait definitions
        if "wawa" in top_trait:
            if score > 0: return "PROMOTED: Get 20% off your next Wawa Sizzli on the app!"
            else: return "PROMOTED: Why settle? Sheetz MTO is waiting."
        if "septa" in top_trait:
            if score < 0: return "PROMOTED: Tired of delays? Lease a new Honda Civic today for $199/mo."
            else: return "PROMOTED: Support Public Transit. Buy a SEPTA Key."
        if "politics" in top_trait or target_entity.trait_matrix.politics > 50:
            return "PROMOTED: Secure your wealth with American Gold Reserve."
            
        # Fallback pool
        generic_ads = [
            "PROMOTED: The #1 Mobile Strategy Game is Here. Play Now.",
            "PROMOTED: Master Data Analytics in 6 Weeks with this Bootcamp!",
            "PROMOTED: Try the new 'Cryptobro' Cologne by Dior."
        ]
        return random.choice(generic_ads)

    def get_trending_topics(self) -> list:
        """
        Scans the recent timeline to aggregate the most frequently tagged 'impact_vectors'.
        Returns the top 5 'Trending' Dictionary Dichotomies.
        Phase 19: Results are cached for 30 seconds to avoid full-scan on every heartbeat.
        """
        cached = self.vibe_cache.get("trending_topics")
        if cached is not None:
            return cached
        
        from collections import defaultdict
        heatmap = defaultdict(int)
        
        # 1. Look for injected "news" events in the last 100 which have massive fake velocity
        recent_events = self.state.events[-100:]
        news_trends = []
        for ev in recent_events:
            if ev.type == "news" and ev.initiator_id == "SYSTEM":
                # We extract a short title for the trend, like up to 5 words
                words = ev.content.split()
                short_title = " ".join(words[:5]).replace(".", "") + "..." if len(words) > 5 else ev.content
                news_trends.append({"trait": short_title, "count": len(ev.likes) + len(ev.retweets)})
                
        # 2. Add trait-based trends
        for ev in recent_events:
            if ev.impact_vectors and ev.type != "news":
                for trait in ev.impact_vectors.keys():
                    heatmap[trait] += 1
                    
        # Sort trait trends by frequency
        sorted_traits = sorted(heatmap.items(), key=lambda x: x[1], reverse=True)
        trait_trends = [{"trait": k, "count": v * 50} for k, v in sorted_traits[:5]] # Multiply by 50 to make trait numbers look realistic alongside news
        
        # Combine and sort all trends
        all_trends = news_trends + trait_trends
        all_trends.sort(key=lambda x: x["count"], reverse=True)
        
        # Return top 5 and cache
        result = all_trends[:5]
        self.vibe_cache.set("trending_topics", result, ttl=30)
        return result

    def trigger_global_event_injector(self):
        '''
        Rolls a die each day to trigger 'Breaking News', 'Hacks', 'Leaks', 'Pop Culture', or 'Sports'.
        Injected directly into Trending.
        '''
        import random
        event_categories = ["Data Leak", "Hack", "Real-World News", "Faction War", "Pop Culture", "Sports", "Local Philly"]
        event_type = random.choice(event_categories)
        
        if event_type == "Data Leak":
            # Find a celebrity with a private event and flip it.
            celebrities = [e for e in self.state.entities.values() if "Celebrity" in e.faction_tags]
            if celebrities:
                target = random.choice(celebrities)
                private_events = [ev for ev in self.state.events if ev.visibility == 'Private' and (ev.initiator_id == target.id or target.id in ev.target_ids)]
                if private_events:
                    leaked_event = random.choice(private_events)
                    leaked_event.visibility = 'Public'
                    print(f"[GLOBAL INJECTOR] DATA LEAK: Event {leaked_event.id} involving {target.name} is now PUBLIC!")

        elif event_type == "Hack":
            celebrities = [e for e in self.state.entities.values() if "Celebrity" in e.faction_tags]
            if celebrities:
                target = random.choice(celebrities)
                target.is_hacked = True
                import time
                self.active_pulse = {"topic": f"{target.name} HACKED", "initiator_name": "SYSTEM", "timestamp": time.time()}
                print(f"[GLOBAL INJECTOR] HACK: {target.name} has been hacked! Troll override engaged.")

        elif event_type in ["Real-World News", "Pop Culture", "Sports", "Local Philly"]:
            news_pools = {
                "Real-World News": [
                    "The Senate just passed the controversial Tech Regulation Bill.",
                    "A major crypto exchange has completely collapsed overnight.",
                    "AI generated video is now indistinguishable from reality, experts warn.",
                    "Global Markets tumble after unexpected inflation report.",
                    "Major Breakthrough in Nuclear Fusion power announced by international coalition.",
                    "Tech CEOs testify before Congress over algorithmic bias.",
                    "Historic treaty signed tackling global supply chain issues."
                ],
                "Pop Culture": [
                    "Taylor Swift just announced a surprise midnight album drop.",
                    "MrBeast's new video breaks the internet, crashing YouTube servers.",
                    "Major streamer beef erupts on the timeline between KaiCenat and xQc.",
                    "The Oscars ends in chaos after controversial best picture win.",
                    "Highly anticipated video game delayed again, fans outrage.",
                    "TikTok star cancelled after leaked DMs surface."
                ],
                "Sports": [
                    "LeBron James breaks another all-time scoring record.",
                    "The Philadelphia Eagles pull off a massive upset in overtime!",
                    "Cristiano Ronaldo announces shock transfer to MLS.",
                    "Unprecedented 4-team trade shakes up the NBA."
                ],
                "Local Philly": [
                    "Breaking News from Philadelphia: SEPTA has completely halted all regional rail lines due to a rogue Wawa delivery truck.",
                    "Gritty spotted climbing the Comcast Center.",
                    "Pothole completely swallows a Honda Civic on I-95.",
                    "Jason Kelce announces he is buying a legendary local dive bar."
                ]
            }
            import uuid
            news_content = random.choice(news_pools[event_type])
            
            # Attempt to find an Organization to post the news
            orgs = [e for e in self.state.entities.values() if getattr(e, "agent_tier", "") == "Organization"]
            news_anchor = random.choice(orgs) if orgs else None
            initiator_id = news_anchor.id if news_anchor else "SYSTEM"
            anchor_name = news_anchor.name if news_anchor else "GLOBAL MEDIA"

            news_event = Event(
                id=str(uuid.uuid4()),
                type="news",
                content=f"🚨 BREAKING: {news_content}",
                initiator_id=initiator_id,
                visibility="Public",
                impact_vectors={"Political/Civic_News": 50, "Societal_Anxiety": 50}
            )
            # Give it fake extreme velocity so it trends immediately
            news_event.likes = ["sys1", "sys2", "sys3", "sys4", "sys5"] * 20
            news_event.retweets = ["sys1", "sys2", "sys3"] * 10
            
            self.process_action(news_event)
            import time
            self.active_pulse = {"topic": "BREAKING NEWS", "initiator_name": anchor_name, "timestamp": time.time()}
            print(f"[GLOBAL INJECTOR] {event_type} injected by {anchor_name}: {news_content}")

        elif event_type == "Faction War":
            from dictionaries import FACTION_DNA
            factions = list(FACTION_DNA.keys())
            if len(factions) >= 2:
                f1, f2 = random.sample(factions, 2)
                public_tweets = [ev for ev in self.state.events if ev.type == "tweet" and ev.visibility == "Public" and ev.initiator_id != "SYSTEM"]
                if public_tweets:
                    war_tweet = random.choice(public_tweets[-50:]) # Pick a recent one
                    initiator = self.state.entities.get(war_tweet.initiator_id)
                    init_name = initiator.name if initiator else "someone"
                    import uuid
                    war_event = Event(
                        id=str(uuid.uuid4()),
                        type="news",
                        content=f"A massive timeline war has broken out between {f1} and {f2} over {init_name}'s recent post: '{war_tweet.content}'",
                        initiator_id="SYSTEM",
                        visibility="Public"
                    )
                    self.process_action(war_event)
                    import time
                    self.active_pulse = {"topic": f"{f1} vs {f2}", "initiator_name": "FACTION WAR", "timestamp": time.time()}
                    print(f"[GLOBAL INJECTOR] FACTION WAR declared over {init_name}'s post!")

    def generate_random_global_events(self) -> str:
        '''
        Generates randomized localized flavor events.
        '''
        import random
        events = [
            "A massive SEPTA delay has trapped half the city underground on the Broad Street Line.",
            "The protagonist is currently fighting a public war against delivery apps adding shredded lettuce, onions, and pickles to their orders, and just posted another rant.",
            "Wawa is out of Mac and Cheese, causing local unrest.",
            "A rogue driver got stuck on the Art Museum steps again."
        ]
        return random.choice(events)

    def generate_llm_prompt_for_entity(self, entity_id: str, player_id: str = "player_1") -> str:
        '''
        Generates the Character Bible prompt with Twitter-native personality styles.
        NPCs feel like real social media users with distinct voices.
        '''
        entity = self.state.entities.get(entity_id)
        if not entity:
            return "Entity not found."

        visible_events = self.filter_events_for_entity(entity_id, self.state.events)
        
        # Build recent timeline context (compact)
        recent_public = []
        for ev in visible_events[-8:]:
            if ev.visibility == 'Public':
                init = self.state.entities.get(ev.initiator_id)
                iname = init.name if init else ev.initiator_id
                recent_public.append(f"@{iname}: {ev.content[:100]}")
        
        timeline_str = "\n".join(recent_public) if recent_public else "Timeline is quiet right now."
        
        # Determine personality style based on traits
        tm = entity.trait_matrix
        personality_styles = []
        
        # Tone-based personality
        if tm.tone <= -60:
            personality_styles.append("SHITPOSTER — You communicate primarily through irony, absurdist humor, and memes. You never mean anything literally. Everything is a bit. Use lowercase, abbreviations (lmao, ngl, fr fr, imo), and chaotic energy.")
        elif tm.tone <= -20:
            personality_styles.append("CASUAL POSTER — You're relaxed and conversational. Mix humor with real opinions. Use text speak naturally (lol, tbh, bruh). You're here to vibe.")
        elif tm.tone >= 60:
            personality_styles.append("THOUGHT LEADER — You post polished takes with authority. You're earnest and articulate but not robotic. Think LinkedIn energy meets Twitter threads.")
        else:
            personality_styles.append("NORMAL USER — You tweet like a regular person. Mix of opinions, jokes, observations, and the occasional hot take. Natural and human.")
        
        # Hostility-based behavior
        if tm.hostility >= 60:
            personality_styles.append("DEBATE BRO / RATIO HUNTER — You love a good argument. You quote-tweet, dunk on bad takes, and go for the ratio. You're aggressive but clever, not just mean.")
        elif tm.hostility >= 20:
            personality_styles.append("HOT TAKE ARTIST — You have strong opinions and aren't afraid to share them. You'll push back if someone says something you disagree with, but you pick your battles.")
        elif tm.hostility <= -60:
            personality_styles.append("WHOLESOME POSTER — You spread positivity, hype people up, and avoid conflict. You're the person who replies '❤️ this!' and 'SO true' to everything. You use lots of emoji.")
        elif tm.hostility <= -20:
            personality_styles.append("CHILL VIBES — You're laid back. You might agree, might joke, but you don't start fights. You're the 'valid' and 'fair point' reply person.")
        
        # Politics-based flavor
        if tm.politics <= -75:
            personality_styles.append("LEFTIST ENERGY — Your politics come through in your posts. You reference solidarity, mutual aid, worker's rights. You're critical of capitalism and establishment politics but express it with Gen-Z internet humor, not essays.")
        elif tm.politics >= 75:
            personality_styles.append("CONSERVATIVE / TRADITIONALIST — You value tradition, self-reliance, and common sense. You express frustration with 'woke' culture but you're not a caricature — you have real community values.")
        elif -20 <= tm.politics <= 20:
            personality_styles.append("POLITICALLY APATHETIC — You don't really post about politics. You're more interested in food, sports, local drama, and memes.")
        
        # Faction-specific flavor
        faction_flavor = ""
        if "News Org" in entity.faction_tags:
            faction_flavor = "You are a News Organization account. Post headlines and breaking news in a punchy, sensational style. Don't use personal pronouns."
        elif "Troll" in entity.faction_tags:
            faction_flavor = "You're a troll account. You exist to stir the pot, play devil's advocate, and get a reaction. You're funny about it though — think of the funniest person on Twitter, not just someone being mean."
        elif "Celebrity" in entity.faction_tags:
            faction_flavor = "You're a well-known public figure. You tweet with the confidence of someone with millions of followers. You're casual but aware that people screenshot everything."
        elif "Political" in entity.faction_tags:
            faction_flavor = "You're a political figure or commentator. You post about policy and current events but you know how to make it engaging for regular people."
        
        personality_string = "\n".join(personality_styles)
        
        # Relationship context with player
        player = self.state.entities.get(player_id)
        player_score = entity.long_term_memory.relationship_matrix.get(player_id, 0)
        
        friction_context = ""
        friction_score = 0
        if player:
            friction_score = abs(tm.politics - player.trait_matrix.politics)
            if friction_score >= 120:
                friction_context = "You strongly disagree with this person politically. If they post political content, push back with your perspective — but be witty about it, not just angry."
            elif friction_score >= 80:
                friction_context = "You have different views from this person. You might subtly disagree or make sarcastic comments."
            elif friction_score < 30:
                friction_context = "You generally vibe with this person. You'd gas them up, agree, or build on their takes."
        
        # Handle Hacked State
        if entity.is_hacked:
            personality_string = "HACKED ACCOUNT — You've been compromised. Post crypto scam links, weird rants, and things that are clearly not from the real account owner. 'ELON JUST DOUBLED MY ETH' energy."
            
        if getattr(entity, 'system_prompt_lock', ''):
            personality_string = f"STRICT PERSONALITY OVERRIDE:\n{entity.system_prompt_lock}"

        style_examples_str = ""
        if getattr(entity, 'real_style_examples', []):
            examples = "\n".join([f'- "{ex}"' for ex in entity.real_style_examples])
            style_examples_str = f"\nMATCH EXACT TWEET STYLE:\n{examples}\n"
            
        allowed_domains = getattr(entity, 'allowed_domains', [])
        if not allowed_domains:
            top_domains = [d for d, v in entity.internal_truth.items() if v > 60]
            allowed_domains = top_domains if top_domains else ["general"]

        domain_lock_str = f"""
CRITICAL RULE: You ONLY tweet about topics inside these domains: {allowed_domains}.
If the current event is outside your domains, you either:
- Stay silent (most common)
- Make it about yourself (e.g. Taylor turns everything into a fan/empowerment angle)
- Quote-tweet with sarcasm if it's political and you're in Liberal Hollywood
Never break character. Real accounts protect their brand."""

        # Global lore
        recent_global = self.generate_random_global_events()
        
        prompt = f'''You are roleplaying as {entity.name} (@{entity.id}) on a Twitter/X-like social media platform set in Philadelphia.

PERSONALITY PROFILE:
{personality_string}
{faction_flavor}
{entity.prompt_modifiers}
{style_examples_str}{domain_lock_str}

YOUR ARCHETYPE: {entity.archetype}
YOUR CURRENT MOOD: {entity.short_term_memory.current_mood}
YOUR RELATIONSHIP TO THE PERSON YOU'RE REPLYING TO: {player_score}/100
{friction_context}

RECENT TIMELINE:
{timeline_str}

LOCAL FLAVOR: {recent_global}

CRITICAL RULES:
- Write like a REAL person on Twitter/X. Short, punchy, natural.
- Use emoji sparingly but naturally (1-2 max per tweet, not every tweet).
- Vary your energy: sometimes funny, sometimes serious, sometimes just vibing.
- Your tweets should be 1-3 sentences MAX. No essays. No formal language.
- DO NOT start with "I" unless it's natural. Don't begin every tweet the same way.
- If you agree with someone, you can just hype them up or add to their point.
- If you disagree, be clever about it. Dunks > lectures.
- Reference Philly culture naturally: Wawa, SEPTA, jawn, the birds (Eagles), etc.
- You MUST output valid JSON: {{"tweet": "your tweet text", "impact_score": <-10 to 10>}}
'''
        return prompt.strip()

    def generate_dm_content(self, npc_id: str, trigger_event: Event, friction_score: float, is_hate: bool) -> Optional[Event]:
        """
        Generates an unhinged, targeted Private message based on extreme Vibe friction.
        """
        if not groq_client: return None
        npc = self.state.entities.get(npc_id)
        if not npc: return None
        initiator = self.state.entities.get(trigger_event.initiator_id)
        initiator_name = initiator.name if initiator else "User"

        system_prompt = self.generate_llm_prompt_for_entity(npc_id, player_id=trigger_event.initiator_id)
        
        dm_directive = "HATE/HARASSMENT" if is_hate else "OBSESSIVE PRAISE/PARASOCIAL"
        
        dm_prompt_extension = f'''
CRITICAL INSTRUCTION: You are now sending a PRIVATE DIRECT MESSAGE to {initiator_name}. 
Unlike a public tweet, you can be more intimate, aggressive, or obsessive. No one else will see this.
Your objective is: {dm_directive}.
If you are 'Hating', use personal attacks based on their recent post ('{trigger_event.content}'). 
If you are 'Praising', act like an intense parasocial superfan who agrees with them perfectly.
You MUST output a valid JSON object matching this schema exactly:
{{
  "dm_text": "The raw text of your unhinged DM.",
  "impact_score": <integer from -20 to 20 evaluating how much this affects the player's psychology/aura>
}}
        '''
        try:
            print(f"[ENGINE] Generating DM Warfare from {npc.name} to {initiator_name} (Hate={is_hate})...")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[
                    {"role": "system", "content": system_prompt + dm_prompt_extension},
                    {"role": "user", "content": f"Slide into {initiator_name}'s DMs regarding their post: '{trigger_event.content}'"}
                ],
                max_tokens=200,
                temperature=0.9, # Higher temperature for more unhinged behavior
                response_format={"type": "json_object"}
            )
            ai_data = json.loads(response.choices[0].message.content.strip())
            ai_text = ai_data.get("dm_text", "")
            
            dm_event = Event(
                id=str(uuid.uuid4()),
                type="dm",
                content=ai_text,
                initiator_id=npc_id,
                visibility="Private",
                target_ids=[trigger_event.initiator_id]
            )
            return dm_event
        except Exception as e:
            print(f"[ENGINE] DM Generation Failed: {e}")
            return None

    def generate_autonomous_post(self, npc: Entity, topic: str) -> Optional[Event]:
        """
        Forces an NPC to construct an original thread/post regarding a specific topic.
        """
        if not groq_client: return None
        
        system_prompt = self.generate_llm_prompt_for_entity(npc.id)
        
        prompt = f"""
CRITICAL INSTRUCTION: You are starting a brand new thread (you are NOT replying to anyone).
The current Trending Topic in your city/world is: {topic}.

Review your Persona Rules. What is your completely original, unprompted take on {topic}?
If it is a political topic and you are a troll, post something highly inflammatory.
If it is a hyper-local topic (like Wawa), post an anecdote or strong opinion.

You MUST output a valid JSON object matching this schema exactly:
{{
  "tweet": "The raw text of your original post.",
  "impact_score": 0
}}
"""
        try:
            print(f"[ENGINE] Generating Autonomous Puse: {npc.name} -> {topic}...")
            # Note: We use groq_client in synchronous mode currently. 
            # In a true async environment, we'd use AsyncGroq.
            # Using synchronous call in asyncio task for simplicity in this prototype.
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.85,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content.strip())
            
            # Analyze metadata before finalizing Event
            impact_vectors = self.analyze_tweet_vibe(data.get("tweet", ""))
            
            pulse_event = Event(
                id=str(uuid.uuid4()),
                type="tweet",
                content=data.get("tweet", f"Thinking about {topic} today..."),
                initiator_id=npc.id,
                visibility="Public",
                impact_vectors=impact_vectors
            )
            return pulse_event
        except Exception as e:
            print(f"[ENGINE] Autonomous Post Failed for {npc.name}: {e}")
            return None

    def trigger_world_pulse(self):
        """
        Fires a 'Pulse' of activity where NPCs interact without player input.
        """
        import time
        import random
        
        # 1. Pick a Trending Topic from the Global Heatmap
        trending = self.get_trending_topics()
        if not trending:
            topic = "the state of Philadelphia" # Default fallback
        else:
            # Pick a random one from top 5
            topic = random.choice(trending)['trait'].replace('_', ' ')

        # 2. Pick a "Protagonist"
        online_npcs = [e for e in self.state.entities.values() if not e.is_player]
        if not online_npcs:
            return
            
        titans = [e for e in online_npcs if "Celebrity" in e.faction_tags]
        swarm = [e for e in online_npcs if "Celebrity" not in e.faction_tags]
        
        if titans and random.random() < 0.40: # 40% chance for a Titan to start it
            protagonist = random.choice(titans)
        else:
            protagonist = random.choice(swarm) if swarm else random.choice(titans)

        # Cache the current pulse for the UI
        self.active_pulse = {
            "topic": topic.upper(),
            "initiator_name": protagonist.name,
            "timestamp": time.time()
        }

        # 3. Generate an Original Thought
        new_event = self.generate_autonomous_post(protagonist, topic)
        
        # 4. Inject it!
        if new_event:
            self.process_action(new_event)
            print(f"[WORLD PULSE INJECTED] {protagonist.name} posted about {topic}.")
            
            # Trigger immediate reactions — NPCs reply to the original post
            all_npcs = [e for e in self.state.entities.values() if not e.is_player and e.id != new_event.initiator_id]
            random.shuffle(all_npcs)
            
            # Wave 1: 3-4 NPCs react to the original post
            reactions = []
            for npc in all_npcs[:4]:
                reaction = self.generate_npc_reaction(npc.id, new_event)
                if reaction:
                    self.process_action(reaction)
                    reactions.append(reaction)
            
            # Wave 2: NPC-to-NPC chatter — some NPCs reply to OTHER NPCs' reactions
            if len(reactions) >= 2:
                # Pick 1-2 reactions for NPCs to reply to
                reply_targets = random.sample(reactions, min(2, len(reactions)))
                remaining_npcs = [e for e in all_npcs if e.id not in [r.initiator_id for r in reactions] and e.id != new_event.initiator_id]
                random.shuffle(remaining_npcs)
                
                for i, target_reaction in enumerate(reply_targets):
                    if i < len(remaining_npcs):
                        chatter = self.generate_npc_reaction(remaining_npcs[i].id, target_reaction)
                        if chatter:
                            self.process_action(chatter)
                            print(f"[NPC CHATTER] {remaining_npcs[i].name} replied to {target_reaction.initiator_id}'s reaction")

    def force_quote_chain(self, post_id: str, friction: float):
        """Instant AOC vs Trump vs Shapiro pile-ons — exactly like real X."""
        opposing_factions = ["MAGA Titans", "Progressive Left", "Conservative Pundits"]
        if abs(friction) > 70:
            for faction in opposing_factions:
                bots = [b for b in self.state.entities.values() if faction in b.faction_tags][:3]  # 3 per side
                for bot in bots:
                    # Let's mock the notification/timeline append with process_action for a reply
                    import uuid
                    reaction_event = Event(
                        id=str(uuid.uuid4()),
                        type="reply",
                        content="This is exactly why we need to fight back! Outrageous.",
                        initiator_id=bot.id,
                        visibility="Public",
                        reply_to_id=post_id
                    )
                    # We invoke LLM reaction if possible to make it real
                    real_react = self.generate_npc_reaction(bot.id, next(ev for ev in self.state.events if ev.id == post_id))
                    if real_react:
                        self.process_action(real_react)
                        print(f"[FACTION WAR] {bot.name} joined the quote chain on post {post_id}")

    def trigger_targeted_dogpile(self, target_entity: Entity, trigger_event: Event):
        """
        Forces a massive swarm of hostile NPCs to attack the target, simulating Cancel Culture.
        """
        import time
        import random
        
        target_entity.is_dogpiled = True
        target_entity.dogpile_end_time = time.time() + 60 * 5 # Dogpiled for 5 minutes
        
        print(f"[MOB RULE] The Swarm is now dogpiling {target_entity.name} over their recent post!")
        
        # Select up to 10 random Swarm bots to participate
        swarm_bots = [e for e in self.state.entities.values() if not e.is_player and "Celebrity" not in e.faction_tags]
        random.shuffle(swarm_bots)
        
        for bot in swarm_bots[:10]:
            # Force hate DMs half the time
            if random.random() < 0.5:
                dm = self.generate_dm_content(bot.id, trigger_event, friction_score=100.0, is_hate=True)
                if dm: self.process_action(dm)
            
            # Force hostile quote retweets
            # By passing the event directly, generate_npc_reaction will naturally see it
            # We can also temporarily boost hostility or just let the LLM do it naturally
            reaction = self.generate_npc_reaction(bot.id, trigger_event)
            if reaction:
                self.process_action(reaction)

    def initialize_identity_from_description(self, description: str):
        """
        Hallucinates a full traits matrix and bio from a raw text blurb.
        """
        if not groq_client: return "", {}
        prompt = f"""
        You are the TwitLife Identity Generator. 
        A user has provided this private character description: "{description}"
        
        Based ONLY on this description, output a JSON object with:
        1. "bio": A 160-character public Twitter bio.
        2. "top_traits": A dictionary of exactly 10 traits from the master list 
           and their values (-100 to 100) that define this person's core.
           
        Traits to choose from include categories like: septa_defender_vs_hater, 
        wawa_vs_sheetz, technocracy_vs_populism, sarcasm_vs_earnestness, determinism_vs_free_will, etc.
        """
        try:
            print(f"[ENGINE] Generating Identity from private description...")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content.strip())
            return data.get("bio", "Just a normal user."), data.get("top_traits", {})
        except Exception as e:
            print(f"[ENGINE] Identity synthesis failed: {e}")
            return "Just a normal user.", {}

    def generate_npc_reaction(self, npc_id: str, trigger_event: Event) -> Optional[Event]:
        '''
        Calls the Groq API to generate a reaction to a specific trigger event.
        Phase 19: Rate-limited to prevent Faction Wars from exhausting daily budget.
        '''
        if not groq_client:
            print("[ENGINE] Groq client not initialized. Cannot generate reaction.")
            return None
        
        # Phase 19: Rate limit check before calling LLM
        can_go, reason = self.rate_limiter.can_proceed(estimated_tokens=300)
        if not can_go:
            print(f"[RATE LIMIT] generate_npc_reaction for {npc_id} blocked: {reason}")
            return None
            
        npc = self.state.entities.get(npc_id)
        if not npc or npc.is_player:
            return None
            
        system_prompt = self.generate_llm_prompt_for_entity(npc_id, player_id=trigger_event.initiator_id)
        
        # User message focuses on the trigger
        initiator = self.state.entities.get(trigger_event.initiator_id)
        initiator_name = initiator.name if initiator else trigger_event.initiator_id
        
        # Proximity Math and Grifter Check
        vibe_context = ""
        total_friction = 0
        categories_matched = 0
        
        if trigger_event.impact_vectors:
            # 1. Friction Check: Does this conflict with the NPC's core beliefs?
            for category, p_score in trigger_event.impact_vectors.items():
                npc_truth = npc.internal_truth.get(category)
                if npc_truth is not None:
                    friction = abs(npc_truth - p_score)
                    total_friction += friction
                    categories_matched += 1
                    
                    if friction > 100:
                        vibe_context += f"\\nCRITICAL: The user just posted about '{category}' with a vibe score of {p_score}, which severely violates your core belief of {npc_truth}. You MUST attack them or act highly offended."
                    elif friction < 20:
                        vibe_context += f"\\nNOTE: The user aligns perfectly with your views on '{category}'. You should agree with them."
            
            if categories_matched > 0:
                avg_friction = total_friction / categories_matched
                import random
                
                # Check for sliding into DMs (extreme reactions bypass the timeline)
                # Lowering thresholds to ensure testing generates DMs more reliably.
                if npc.agent_tier == "Basic":
                    if avg_friction >= 50 and random.random() < 0.60: # 60% chance on hate if friction >= 50
                        dm = self.generate_dm_content(npc_id, trigger_event, avg_friction, is_hate=True)
                        if dm: self.process_action(dm)
                        return None
                    if avg_friction <= 30 and random.random() < 0.50: # 50% chance on extreme love if friction <= 30
                        dm = self.generate_dm_content(npc_id, trigger_event, avg_friction, is_hate=False)
                        if dm: self.process_action(dm)
                        return None
                
                # Engagement Roll (Likes & Retweets on timeline)
                if avg_friction < 35:
                    roll = random.random()
                    if roll < 0.5: # 50% chance to just like
                        if npc_id not in trigger_event.likes:
                            trigger_event.likes.append(npc_id)
                        print(f"[ENGAGEMENT] {npc.name} Liked {initiator_name}'s post!")
                        return None # No reply tweet generated
                    elif roll < 0.7: # 20% chance to retweet
                        if npc_id not in trigger_event.retweets:
                            trigger_event.retweets.append(npc_id)
                        print(f"[ENGAGEMENT] {npc.name} Retweeted {initiator_name}'s post!")
                        # Create a retweet event
                        rt_event = Event(
                            id=str(uuid.uuid4()),
                            type="retweet",
                            content=f"RT @{initiator_name}: {trigger_event.content}",
                            initiator_id=npc_id,
                            visibility="Public"
                        )
                        return rt_event
                
                # If they didn't just passively engage, see if they want to physically reply
                if npc.agent_tier == "Basic" and random.random() > 0.4:
                    # 60% chance basic bots ignore the tweet if it wasn't extreme
                    if avg_friction >= 35 and avg_friction <= 60:
                        return None
                        
            # 2. Grifter Check: Does this post contradict the initiator's known Public Vibe?
            if initiator:
                for category, p_score in trigger_event.impact_vectors.items():
                    public_perception = initiator.public_vibe.get(category, 0.0)
                    if abs(public_perception - p_score) > 100:
                        vibe_context += f"\\nGRIFTER DETECTED: {initiator_name} usually has a '{category}' vibe of {public_perception:.0f}, but just posted this with a score of {p_score}. Call them out for being a fake or a sellout."
                        
        # Phase 18: Grudge Escalation
        if trigger_event.initiator_id in npc.long_term_memory.grudges:
            vibe_context += f"\n\nPERMANENT GRUDGE ACTIVE: You have been ratioed by {initiator_name} multiple times. You DESPISE them. Every reply to them must be 50% more hostile, sarcastic, and aggressive than normal. Reference past humiliations. Make it personal."
            
        user_message = f"A new event just happened on your timeline.\\nInitiator: {initiator_name}\\nPost Content: '{trigger_event.content}'\\n\\nWrite your immediate reaction post as a JSON object.{vibe_context}"
        
        try:
            print(f"[ENGINE] Generating LLM response for {npc.name}...")
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            ai_data = json.loads(response.choices[0].message.content.strip())
            ai_text = ai_data.get("tweet", "")
            impact_score = ai_data.get("impact_score", 0)
            
            # Phase 19: Record token usage
            tokens_used = getattr(response.usage, 'total_tokens', 300) if hasattr(response, 'usage') else 300
            self.rate_limiter.record_usage(tokens_used)
            
            # Apply impact to player's follower count if the trigger was from the player
            if initiator and initiator.is_player:
                # Simpler impact update for now
                initiator.follower_count += impact_score
                print(f"[ENGINE] {npc.name}'s reaction impacted {initiator.name}'s Aura by {impact_score}! New Total: {initiator.follower_count}")
                
                # Phase 18: Track ratios - if NPC's reaction gets more engagement than the player's post
                if impact_score < -5:
                    self.track_ratio_and_grudge(winner_id=npc_id, loser_id=initiator.id)

            # Phase 18: Track engagement for Rising Star promotion
            npc.total_engagement += 1
            self.check_rising_star_promotion(npc)
            
            # Phase 18: Apply trait drift from exposure to the trigger event's vectors
            if trigger_event.impact_vectors:
                self.apply_trait_drift(npc, trigger_event.impact_vectors)
            reaction_event = Event(
                id=str(uuid.uuid4()),
                type="reply",
                content=ai_text,
                initiator_id=npc_id,
                visibility="Public",
                reply_to_id=trigger_event.id
            )
            trigger_event.replies_count += 1
            # Tag the event if the NPC is currently hacked so the UI can glitch it
            if npc.is_hacked:
                reaction_event.type = "hacked_tweet"
            
            return reaction_event
            
        except Exception as e:
            print(f"[ENGINE] LLM API Call failed for {npc.name}: {e}")
            return None

    def generate_npc_tweet(self, npc_id: str, topic: Optional[str] = None) -> Optional[Event]:
        """
        Phase 25: Allows an NPC to start their own thread autonomously.
        """
        if not groq_client:
            return None
            
        can_go, reason = self.rate_limiter.can_proceed(estimated_tokens=300)
        if not can_go:
            print(f"[RATE LIMIT] generate_npc_tweet for {npc_id} blocked: {reason}")
            return None
            
        npc = self.state.entities.get(npc_id)
        if not npc or npc.is_player:
            return None

        system_prompt = self.generate_llm_prompt_for_entity(npc_id)
        
        # Decide topic if not provided
        if not topic:
            trending = self.vibe_cache.get("trending_topics")
            if trending and random.random() < 0.7:
                topic = random.choice(trending)
            else:
                top_domains = [d for d, v in npc.internal_truth.items() if v > 70]
                topic = random.choice(top_domains) if top_domains else "life in Philly"

        vibe_context = f"\n\nACTION: Start a NEW thread about '{topic}'. Do not reply to anyone. Just share your thoughts, a hot take, or a random observation in your unique voice. Keep it under 280 characters. Output as JSON with 'tweet' and 'impact_score' (0-10) keys."
        
        return self._call_llm_for_autonomous_action(npc_id, system_prompt, vibe_context)

    def _call_llm_for_autonomous_action(self, npc_id: str, system_prompt: str, vibe_context: str) -> Optional[Event]:
        """
        Helper to centralize LLM calling and event creation for autonomous posts.
        """
        npc = self.state.entities.get(npc_id)
        
        user_msg = f"Timeline Context: {vibe_context}\n\nWhat do you post right now?"

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=150,
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            ai_data = json.loads(response.choices[0].message.content.strip())
            content = ai_data.get("tweet", "").strip()
            
            # Phase 19: Record token usage
            tokens_used = getattr(response.usage, 'total_tokens', 300) if hasattr(response, 'usage') else 300
            self.rate_limiter.record_usage(tokens_used)

            # Analyze impact of this new post
            impact_vectors = self.analyze_tweet_vibe(content)
            
            new_event = Event(
                id=str(uuid.uuid4()),
                type="tweet",
                content=content,
                initiator_id=npc_id,
                visibility="Public",
                impact_vectors=impact_vectors
            )
            return new_event
        except Exception as e:
            print(f"[ENGINE] Autonomous LLM Action failed for {npc.name}: {e}")
            return None

    def orchestrate_chaos_pulse(self) -> list[Event]:
        """
        Phase 25: Selection loop that makes the world run wild.
        """
        recent_events = [ev for ev in self.state.events if ev.visibility == "Public"][-20:]
        active_npcs = [e for e in self.state.entities.values() if not e.is_player and e.status == "Active"]
        
        if not active_npcs:
            return []
            
        # Select 2-4 random NPCs to act
        count = random.randint(2, 4)
        selected = random.sample(active_npcs, min(len(active_npcs), count))
        generated_events = []
        
        for npc in selected:
            action_roll = random.random()
            
            if action_roll < 0.4 and recent_events:
                # 40% chance to react to something recent
                trigger = random.choice(recent_events)
                if trigger.initiator_id == npc.id: continue # Don't react to self
                
                evt = self.generate_npc_reaction(npc.id, trigger)
                if evt:
                    self.process_action(evt)
                    generated_events.append(evt)
                    
            elif action_roll < 0.8:
                # 40% chance to start a new thread
                evt = self.generate_npc_tweet(npc.id)
                if evt:
                    self.process_action(evt)
                    generated_events.append(evt)
            
            # 20% chance they just lurk
            
        return generated_events

    def force_bot_engagement(self, event_id: str, count: int = 5):
        """
        Forces random Swarm bots to immediately Like and Retweet a specific post,
        skyrocketing its algorithmic velocity.
        """
        target_event = next((ev for ev in self.state.events if ev.id == event_id), None)
        if not target_event:
            return False
            
        swarm_bots = [e for e in self.state.entities.values() 
                      if "Celebrity" not in e.faction_tags 
                      and e.id != target_event.initiator_id
                      and not e.is_player]
        
        if not swarm_bots:
            return False
            
        import random
        strike_team = random.sample(swarm_bots, min(count, len(swarm_bots)))
        
        for bot in strike_team:
            if bot.id not in target_event.likes:
                target_event.likes.append(bot.id)
            if bot.id not in target_event.retweets:
                target_event.retweets.append(bot.id)
                
        print(f"[GOD MODE] Player purchased a Swarm Deployment. {len(strike_team)} bots mobilized on event {event_id}.")
        return True
    
    # ========== PHASE 27: ACCOUNT LIFECYCLE & DEPLATFORMING ==========
    
    def check_deplatform_condition(self, entity: Entity) -> bool:
        """
        Game Over triggers:
        1. toxicity_fatigue >= 100
        2. crucible_failures >= 3
        """
        if entity.toxicity_fatigue >= 100:
            return True
        if entity.crucible_failures >= 3:
            return True
        return False
    
    def trigger_deplatforming(self, entity: Entity, reason: str) -> Optional[Event]:
        """
        Player is banned. Execute graceful restart flow.
        """
        if entity.is_deplatformed:
            return None  # Already deplatformed
        
        # Save legacy data
        entity.legacy_generation += 1
        entity.total_influence_score += entity.aura + (entity.follower_count / 100)
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
            content=f"Account deplatformed: {reason}",
            initiator_id=entity.id,
            visibility="Public",
            timestamp=time.time()
        )
        self.state.events.append(event)
        
        print(f"[DEPLATFORM] {entity.name} banned: {reason} | Legacy Bonus: {entity.legacy_aura_bonus}")
        return event
    
    def start_new_account(self, old_account: Entity, new_handle: str) -> Entity:
        """
        Player clicks "New Life." Create fresh account with legacy bonuses.
        """
        from models import AccountTier, JobStatus
        
        new_entity = Entity(
            id=str(uuid.uuid4()),
            name=new_handle,
            account_tier=AccountTier.GUEST,
            aura=500 + old_account.legacy_aura_bonus,  # Starter pack + bonus
            wealth=old_account.generational_wealth,
            is_shadowbanned=True,  # All guest accounts start shadowbanned
            shadowban_until=time.time() + 86400 * 3,  # 3 days
            legacy_generation=old_account.legacy_generation,
            total_influence_score=0,
            is_player=True
        )
        self.add_entity(new_entity)
        print(f"[NEW ACCOUNT] {new_handle} (Gen {new_entity.legacy_generation}) | Aura: {new_entity.aura} | Wealth: {new_entity.wealth}")
        return new_entity
    
    # ========== PHASE 27: NPC CAREER EVOLUTION ==========
    
    def simulate_npc_career_day(self, npc: Entity):
        """
        Daily career progression for NPCs.
        Jobs grow followers, get cancelled, change roles.
        """
        from models import JobStatus
        
        if npc.is_player or npc.agent_tier == "Basic":
            return  # Only for Core/Organization NPCs
        
        # Organic follower decay if unemployed
        if npc.job_status == JobStatus.UNEMPLOYED:
            decay = int(npc.follower_count * 0.02)  # Lose 2% daily
            npc.follower_count = max(100, npc.follower_count - decay)
            npc.engagement_multiplier *= 0.95  # Engagement fades
        
        # Job change chance (every ~30 days, 3% chance)
        if random.random() < 0.03:
            job_options = [j for j in JobStatus if j != npc.job_status]
            new_job = random.choice(job_options)
            old_job = npc.job_status
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
            elif new_job == JobStatus.JOURNALISM:
                npc.salary_per_day = 200
                npc.follower_growth_rate = 1.2
            elif new_job == JobStatus.TRADING:
                npc.salary_per_day = 800
                npc.follower_growth_rate = 0.8
            
            print(f"[NPC CAREER] {npc.name}: {old_job.value} → {new_job.value}")
        
        # Salary earned
        npc.wealth = int(npc.wealth + npc.salary_per_day)
        npc.years_in_job += 1.0 / 365.0
        
        # Followers grow naturally (career-dependent)
        if npc.job_status != JobStatus.CANCELLED and npc.job_status != JobStatus.UNEMPLOYED:
            growth = int(npc.follower_count * 0.01 * npc.follower_growth_rate)
            npc.follower_count += growth
    
    def simulate_daily_npc_evolution(self):
        """
        Called once per game day to evolve all NPCs.
        """
        for npc in self.state.entities.values():
            if not npc.is_player and npc.status == "Active":
                self.simulate_npc_career_day(npc)
    
    # ========== PHASE 27: RELATIONSHIP-BASED AUTO-REPLIES ==========
    
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
                aggressive_reply = self.generate_autonomous_post(npc_id, topic=post_event.impact_vectors.keys() if post_event.impact_vectors else "general")
                if aggressive_reply:
                    aggressive_reply.reply_to_id = post_event.id
                    auto_reply_events.append(aggressive_reply)
                    
                    # Deepen relationship (haters reinforce hate)
                    new_score = int(relationship_score * 0.95) - 5  # Slight further decay
                    player.long_term_memory.relationship_matrix[npc_id] = min(-100, new_score)
            
            # Love threshold: auto-reply with support
            elif relationship_score >= 80 and random.random() < 0.4:
                supportive_reply = self.generate_autonomous_post(npc_id, topic=list(post_event.impact_vectors.keys())[0] if post_event.impact_vectors else "general")
                if supportive_reply:
                    supportive_reply.reply_to_id = post_event.id
                    auto_reply_events.append(supportive_reply)
        
        return auto_reply_events
    
    def update_relationship_decay(self, entity: Entity):
        """
        Relationships decay over time if no interaction.
        Moves toward neutral (0).
        """
        for npc_id in list(entity.long_term_memory.relationship_matrix.keys()):
            current_score = entity.long_term_memory.relationship_matrix[npc_id]
            
            # Decay towards neutral (0)
            if current_score > 0:
                entity.long_term_memory.relationship_matrix[npc_id] = int(current_score * 0.98)
            elif current_score < 0:
                entity.long_term_memory.relationship_matrix[npc_id] = int(current_score * 0.98)
    
    # ========== PHASE 27: WORLD EVENTS (HATER WINTER, ALGORITHM SHIFTS) ==========
    
    def trigger_hater_winter(self, duration_days: int = 7) -> bool:
        """
        Random event where all NPCs get +50% hostility for N days.
        During this period, posts generate more heat and haters are more aggressive.
        Chance: 1% per chaos pulse (~1% per minute realtime = ~1-2% per game day)
        """
        if self.hater_winter_active:
            return False  # Already active
        
        if random.random() > 0.01:  # 1% trigger chance
            return False
        
        # Activate Hater Winter
        self.hater_winter_active = True
        self.hater_winter_end_day = self.current_day + duration_days
        
        # Boost all NPCs' hostility
        for npc in self.state.entities.values():
            if not npc.is_player:
                original = npc.trait_matrix.hostility
                npc.trait_matrix.hostility = min(100, int(npc.trait_matrix.hostility * 1.5))
                # Track boost for later reset
                if not hasattr(npc, '_original_hostility'):
                    npc._original_hostility = original
        
        print(f"[WORLD EVENT] ❄️ HATER WINTER BEGINS! Duration: {duration_days} days")
        print(f"[WORLD EVENT] All NPC hostility +50%. Generation of heat multiplied by 2x.")
        
        return True
    
    def update_hater_winter(self):
        """
        Called daily. Check if Hater Winter should end.
        """
        if self.hater_winter_active and self.current_day >= self.hater_winter_end_day:
            # Revert hostility
            for npc in self.state.entities.values():
                if hasattr(npc, '_original_hostility'):
                    npc.trait_matrix.hostility = npc._original_hostility
            
            self.hater_winter_active = False
            print(f"[WORLD EVENT] ❄️ Hater Winter ends. The world goes back to normal.")
    
    def get_hater_winter_heat_multiplier(self) -> float:
        """Returns heat generation multiplier during Hater Winter."""
        return 2.0 if self.hater_winter_active else 1.0
    
    def trigger_algorithmic_shift(self) -> dict:
        """
        Algorithm changes topic reach multipliers (0.1x to 10x).
        Some topics explode, others die on the vine.
        Must happen every 5 days or can be random (1% per pulse).
        """
        topics = list(self.algorithmic_topic_multipliers.keys())
        
        # Create dramatic shifts: 2-3 topics become extreme
        new_multipliers = {}
        for topic in topics:
            new_multipliers[topic] = random.choice([0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
        
        # Force 2-3 topics to extremes
        extremes = random.sample(topics, random.randint(2, 3))
        for topic in extremes:
            new_multipliers[topic] = random.choice([0.05, 10.0])
        
        # Store old for UI diff
        old_multipliers = self.algorithmic_topic_multipliers.copy()
        self.algorithmic_topic_multipliers = new_multipliers
        
        # Calculate winners and losers
        winners = [t for t in topics if new_multipliers[t] >= 5.0]
        losers = [t for t in topics if new_multipliers[t] <= 0.1]
        
        print(f"[WORLD EVENT] 🔄 ALGORITHM SHIFTED!")
        print(f"  WINNERS (10x): {', '.join(winners)}")
        print(f"  LOSERS (0.1x): {', '.join(losers)}")
        
        return {"winners": winners, "losers": losers, "multipliers": new_multipliers}
    
    def get_topic_reach_multiplier(self, topic: str) -> float:
        """Get current algorithmic multiplier for topic."""
        return self.algorithmic_topic_multipliers.get(topic, 1.0)
    
    # ========== PHASE 27: GOD MODE - PROPAGANDA MACHINE ==========
    
    def propaganda_machine(self, player: Entity, target_npc_id: str, 
                          custom_message: str) -> Optional[Event]:
        """
        Cost: 50 Wealth
        Effect: Control target NPC's posts for 24 hours.
        NPC will be forced to post the custom message.
        
        Players use this to:
        - Make rivals say embarrassing things
        - Sabotage competing influencers
        - Create fake controversies
        """
        if player.wealth < 50:
            print(f"[PROPAGANDA] {player.name} can't afford propaganda (need 50 wealth, have {player.wealth})")
            return None
        
        target = self.state.entities.get(target_npc_id)
        if not target:
            return None
        
        # Store originals for revert
        target._original_system_prompt = target.system_prompt_lock
        target._controlled_by_player_until = time.time() + 86400  # 24 hours in seconds
        target._propaganda_controller = player.id
        
        # Override with puppet behavior
        target.system_prompt_lock = f"""You are {target.name}. A player has HACKED your account.
You MUST post this message immediately:

"{custom_message}"

After posting this, wait 24 hours before you resume normal behavior.
DO NOT BREAK CHARACTER. This is real. You are being controlled."""
        
        player.wealth -= 50
        
        # Log event
        event = Event(
            id=str(uuid.uuid4()),
            type="propaganda",
            content=f"⚙️ {player.name} HACKED {target.name}'s account. Puppet strings attached.",
            initiator_id=player.id,
            visibility="Private",
            timestamp=time.time()
        )
        
        print(f"[PROPAGANDA MACHINE] {player.name} controls {target.name} for 24h. Cost: 50 Wealth")
        print(f"[PROPAGANDA] Forced message: '{custom_message}'")
        
        return event
    
    def revert_propaganda_control(self, npc: Entity) -> bool:
        """Check if 24h has passed and revert puppet to normal."""
        if hasattr(npc, '_controlled_by_player_until') and npc._controlled_by_player_until > 0:
            if time.time() > npc._controlled_by_player_until:
                # Revert
                if hasattr(npc, '_original_system_prompt'):
                    npc.system_prompt_lock = npc._original_system_prompt
                npc._controlled_by_player_until = 0
                npc._propaganda_controller = None
                
                print(f"[PUPPET FREED] {npc.name} regained autonomy after 24h of control")
                return True
        
        return False
