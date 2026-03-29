from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import asyncio
import random
import time
from typing import List, Optional

from models import GameState, Entity, Event, TraitMatrix
from engine import GameEngine
from npc_seeder import seed_population
from gamification import (
    calculate_influence_rank, check_achievements, DAILY_QUESTS, 
    generate_daily_event, calculate_vanguard_ranks,
    calculate_market_cost, calculate_monetization_reward
)
from follower_algorithm import calculate_organic_engagement

app = FastAPI(title="TwitLife API")

# Enable CORS for Next.js frontend (local + Vercel production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://twittlife.vercel.app",
        "https://twittlife-*.vercel.app",  # Preview deployments
        "https://twittlife-git-*.vercel.app",  # Git branch deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Global State
state = GameState()
engine = GameEngine(state)

active_connections = []
chaos_mode_enabled = True

async def chaos_pulse_daemon():
    """
    Phase 25: Autonomous background task that triggers NPC activity.
    """
    print("[CHAOS] Autonomous Loop Started.")
    while True:
        try:
            if chaos_mode_enabled:
                # Random delay to simulate organic activity
                delay = random.randint(45, 90)
                await asyncio.sleep(delay)
                events = engine.orchestrate_chaos_pulse()
                if events:
                    print(f"[CHAOS] Triggered autonomous pulse: {len(events)} events generated.")
            else:
                await asyncio.sleep(30)
        except Exception as e:
            print(f"[CHAOS] Error in daemon: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    # Phase 25: Trigger an immediate pulse in the background
    print("[CHAOS] Booting Autonomous Network...")
    async def run_initial_pulse():
        await asyncio.sleep(2) # Give uvicorn a second to finish starting
        engine.orchestrate_chaos_pulse()
    asyncio.create_task(run_initial_pulse())
    asyncio.create_task(chaos_pulse_daemon())

@app.websocket("/ws/timeline")
async def websocket_timeline(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

def broadcast_sync(event):
    if not active_connections:
        return
    initiator = state.entities.get(event.initiator_id)
    payload = {
        "id": event.id,
        "type": event.type,
        "content": event.content,
        "initiator_id": event.initiator_id,
        "initiator_name": initiator.name if initiator else "Unknown",
        "initiator_archetype": initiator.archetype if initiator else "",
        "is_verified": getattr(initiator, "is_verified", False),
        "visibility": event.visibility,
        "timestamp": event.timestamp,
        "likes_count": len(event.likes),
        "retweets_count": len(event.retweets),
        "replies_count": 0,
        "reply_to_id": getattr(event, 'reply_to_id', None),
        "media_url": getattr(event, 'media_url', None)
    }
    
    async def _send():
        for conn in list(active_connections):
            try:
                await conn.send_json({"type": "new_event", "payload": payload})
            except Exception:
                if conn in active_connections:
                    active_connections.remove(conn)

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_send())
    except RuntimeError:
        pass

engine.on_new_event = broadcast_sync

from database import SessionLocal, SavedEntity, SavedEvent

db = SessionLocal()
saved_entities = db.query(SavedEntity).all()
saved_events = db.query(SavedEvent).all()

if not saved_entities:
    print("[DB] No saved state found. Booting TwitLife Simulation...")
    # 1. Spawn the Player
    player = Entity(
        id="player_1", 
        name="Alex", 
        is_player=True, 
        archetype="The Protagonist", 
        trait_matrix=TraitMatrix(politics=0, tone=50, hostility=0),
        internal_truth={},
        public_vibe={}
    )
    engine.add_entity(player)

    # 2. Seed the initial population of celebrities + bots
    initial_population = seed_population(num_swarm=1200)
    for entity in initial_population:
        engine.add_entity(entity)

    # Save Entities to SQLite
    for entity in state.entities.values():
        db.add(SavedEntity(id=entity.id, data=entity.model_dump() if hasattr(entity, 'model_dump') else entity.dict()))
    db.commit()

    # Add some seed events
    e1 = Event(id=str(uuid.uuid4()), type="tweet", content="Just arrived on the timeline! Ready to explore.", initiator_id="player_1", visibility="Public")
    e2 = Event(id=str(uuid.uuid4()), type="tweet", content="Coffee price is up again. The end is near. #Economy", initiator_id="banksy", visibility="Public")
    engine.process_action(e1)
    engine.process_action(e2)
    
    db.add(SavedEvent(id=e1.id, data=e1.model_dump() if hasattr(e1, 'model_dump') else e1.dict()))
    db.add(SavedEvent(id=e2.id, data=e2.model_dump() if hasattr(e2, 'model_dump') else e2.dict()))
    db.commit()
else:
    print(f"[DB] Restoring {len(saved_entities)} entities and {len(saved_events)} events from SQLite...")
    for se in saved_entities:
        engine.add_entity(Entity(**se.data))
    for se in saved_events:
        state.events.append(Event(**se.data))

db.close()

def save_state_to_db():
    try:
        _db = SessionLocal()
        for entity in state.entities.values():
            _db.merge(SavedEntity(id=entity.id, data=entity.model_dump() if hasattr(entity, 'model_dump') else entity.dict()))
        for event in state.events:
            _db.merge(SavedEvent(id=event.id, data=event.model_dump() if hasattr(event, 'model_dump') else event.dict()))
        _db.commit()
        _db.close()
    except Exception as e:
        print(f"[DB ERROR] Save failed: {e}")

class RegisterRequest(BaseModel):
    handle: str
    name: str
    description: str = ""
    primary_niche: str = "general"

@app.post("/api/register")
def register_player(req: RegisterRequest):
    """
    Registers a new player entity with the chosen handle.
    If the handle already exists, returns the existing entity's info.
    """
    existing = state.entities.get(req.handle)
    if existing:
        return {"status": "exists", "handle": req.handle, "aura": existing.follower_count, "credits": existing.credits}
    
    new_player = Entity(
        id=req.handle,
        name=req.name,
        is_player=True,
        archetype="The Protagonist",
        primary_niche=req.primary_niche,
        trait_matrix=TraitMatrix(politics=0, tone=50, hostility=0),
        internal_truth={},
        public_vibe={},
        follower_count=1500
    )
    engine.add_entity(new_player)
    
    # If they provided a secret description, generate their identity
    if req.description.strip():
        try:
            bio, top_traits = engine.initialize_identity_from_description(req.description)
            new_player.private_description = req.description
            new_player.bio = bio
            new_player.internal_truth.update(top_traits)
            new_player.public_vibe.update(top_traits)
        except Exception as e:
            new_player.private_description = req.description
            new_player.bio = req.description
            print(f"[REGISTER] Identity generation failed: {e}")
    
    return {"status": "created", "handle": req.handle, "aura": new_player.follower_count, "credits": new_player.credits}


class PostTweetRequest(BaseModel):
    initiator_id: str
    content: str
    visibility: str = "Public"
    target_ids: List[str] = []
    reply_to_id: str = None
    media_url: str = None

@app.get("/api/timeline")
def get_timeline(entity_id: str = "player_1"):
    """
    Returns the timeline formatted for the requested entity.
    Filters out replies from the main feed so they only show in thread detail views.
    """
    entity = state.entities.get(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    raw_ranked_events = engine.get_ranked_timeline(entity_id, limit=100)
    
    # Filter out embedded replies from the main timeline feed
    main_feed_timeline = [ev for ev in raw_ranked_events if getattr(ev, 'reply_to_id', None) is None][:50]
        
    feed = []
    for ev in main_feed_timeline:
        initiator = state.entities.get(ev.initiator_id)
        name = initiator.name if initiator else "Unknown"
        archetype = initiator.archetype if initiator else ""
        # Count replies to this event
        replies_count = sum(1 for e in state.events if getattr(e, 'reply_to_id', None) == ev.id)
        feed.append({
            "id": ev.id,
            "type": ev.type,
            "content": ev.content,
            "initiator_id": ev.initiator_id,
            "initiator_name": name,
            "initiator_archetype": archetype,
            "is_verified": getattr(initiator, "is_verified", False),
            "initiator_aura": getattr(initiator, "aura", 1500),
            "initiator_aura_debt": getattr(initiator, "aura_debt_posts", 0),
            "visibility": ev.visibility,
            "timestamp": ev.timestamp,
            "likes_count": len(ev.likes),
            "retweets_count": len(ev.retweets),
            "replies_count": max(getattr(ev, 'replies_count', 0), replies_count),
            "reply_to_id": getattr(ev, 'reply_to_id', None),
            "media_url": getattr(ev, 'media_url', None)
        })

    # Get the top 5 shifting vibes for the Vibe Radar UI
    top_vibes = []
    if entity.public_vibe:
        sorted_vibes = sorted(entity.public_vibe.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        top_vibes = [{"trait_name": k, "score": float(v)} for k, v in sorted_vibes]

    return {
        "timeline": feed,
        "player_aura": getattr(entity, 'aura', 1500),
        "player_wealth": getattr(entity, 'wealth', 0),
        "player_heat": getattr(entity, 'heat', 0),
        "follower_count": getattr(entity, 'follower_count', 0),
        "player_vibe": top_vibes,
        "is_dogpiled": getattr(entity, 'is_dogpiled', False),
        "simulated_credits": getattr(entity, 'simulated_credits', 0),
        "simulation_day": getattr(engine, 'current_day', 0),
        "simulation_era": engine.simulation_era,
        "monthly_income_breakdown": getattr(entity, 'monthly_income_breakdown', {})
    }


class LikeRequest(BaseModel):
    entity_id: str
    event_id: str

@app.post("/api/like")
def like_tweet(req: LikeRequest):
    """Persist a like from an entity on a specific event."""
    event = next((ev for ev in state.events if ev.id == req.event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if req.entity_id not in event.likes:
        event.likes.append(req.entity_id)
        
        # Phase 22 Gamification Hook
        author = state.entities.get(event.initiator_id)
        if author:
            author.total_engagement = getattr(author, 'total_engagement', 0) + 1
            author.influence_rank = calculate_influence_rank(author)
            check_achievements(author)
            
    return {"likes_count": len(event.likes)}


class RetweetRequest(BaseModel):
    entity_id: str
    event_id: str

@app.post("/api/retweet")
def retweet_tweet(req: RetweetRequest):
    """Persist a retweet from an entity on a specific event."""
    event = next((ev for ev in state.events if ev.id == req.event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if req.entity_id not in event.retweets:
        event.retweets.append(req.entity_id)
        
        # Phase 22 Gamification Hook
        author = state.entities.get(event.initiator_id)
        if author:
            author.total_engagement = getattr(author, 'total_engagement', 0) + 1
            author.influence_rank = calculate_influence_rank(author)
            check_achievements(author)

    return {"retweets_count": len(event.retweets)}


@app.get("/api/tweet/{tweet_id}")
def get_tweet_detail(tweet_id: str):
    """Returns a single tweet plus all its threaded replies."""
    parent = next((ev for ev in state.events if ev.id == tweet_id), None)
    if not parent:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    initiator = state.entities.get(parent.initiator_id)
    name = initiator.name if initiator else "Unknown"
    archetype = initiator.archetype if initiator else ""
    
    # Gather all replies
    replies = []
    for ev in state.events:
        if getattr(ev, 'reply_to_id', None) == tweet_id:
            rep_initiator = state.entities.get(ev.initiator_id)
            rep_name = rep_initiator.name if rep_initiator else "Unknown"
            rep_arch = rep_initiator.archetype if rep_initiator else ""
            sub_replies_count = sum(1 for e in state.events if getattr(e, 'reply_to_id', None) == ev.id)
            replies.append({
                "id": ev.id,
                "type": ev.type,
                "content": ev.content,
                "initiator_id": ev.initiator_id,
                "initiator_name": rep_name,
                "initiator_archetype": rep_arch,
                "is_verified": getattr(rep_initiator, "is_verified", False),
                "timestamp": ev.timestamp,
                "likes_count": len(ev.likes),
                "retweets_count": len(ev.retweets),
                "replies_count": sub_replies_count,
                "reply_to_id": getattr(ev, 'reply_to_id', None),
                "media_url": getattr(ev, 'media_url', None)
            })
    
    replies.sort(key=lambda x: x["timestamp"])
    replies_count = len(replies)
    
    return {
        "tweet": {
            "id": parent.id,
            "type": parent.type,
            "content": parent.content,
            "initiator_id": parent.initiator_id,
            "initiator_name": name,
            "initiator_archetype": archetype,
            "is_verified": getattr(initiator, "is_verified", False),
            "timestamp": parent.timestamp,
            "likes_count": len(parent.likes),
            "retweets_count": len(parent.retweets),
            "replies_count": replies_count,
            "reply_to_id": parent.reply_to_id
        },
        "replies": replies
    }

@app.get("/api/notifications")
def get_notifications(entity_id: str):
    entity = state.entities.get(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    notifications = []
    # Find events where the entity is the initiator and people liked/retweeted
    # Or find replies to the entity's posts (we check if a post mentions them or is a quote RT)
    for ev in state.events:
        if ev.initiator_id == entity_id:
            for liker_id in ev.likes:
                liker = state.entities.get(liker_id)
                lname = liker.name if liker else liker_id
                notifications.append({
                    "id": f"like_{ev.id}_{liker_id}",
                    "type": "like",
                    "content": f"{lname} liked your post: '{ev.content}'",
                    "actor_name": lname,
                    "timestamp": ev.timestamp
                })
            for rter_id in ev.retweets:
                rter = state.entities.get(rter_id)
                rname = rter.name if rter else rter_id
                notifications.append({
                    "id": f"rt_{ev.id}_{rter_id}",
                    "type": "retweet",
                    "content": f"{rname} retweeted your post: '{ev.content}'",
                    "actor_name": rname,
                    "timestamp": ev.timestamp
                })
        else:
            # Check for replies / quote RTs referencing the player
            if f"@{entity.name}" in ev.content or (f"RT @{entity.name}" in ev.content):
                actor = state.entities.get(ev.initiator_id)
                aname = actor.name if actor else ev.initiator_id
                notifications.append({
                    "id": f"tag_{ev.id}",
                    "type": "mention",
                    "content": f"{aname} mentioned you: '{ev.content}'",
                    "actor_name": aname,
                    "timestamp": ev.timestamp
                })

    # Sort notifications by newest first (approx. by reverse order)
    notifications.reverse()
    return {"notifications": notifications[:50]}

@app.get("/api/trending")
def get_trending():
    """
    Returns the top 5 trending topics (can be dictionary traits or global news events).
    """
    trends = engine.get_trending_topics()
    
    # The new trends can be dicts with "trait" (news events or trait trends) and "count".
    formatted_trends = []
    for t in trends:
        if isinstance(t, dict):
            name = str(t.get("trait", "Unknown")).replace("_", " ").title()
            count = t.get("count", 0)
            if count > 0:
                formatted_trends.append(f"{name} ({count} posts)")
            else:
                formatted_trends.append(name)
        else:
            formatted_trends.append(str(t).replace("_", " ").title())
            
    return {"trending": formatted_trends}

@app.post("/api/advance_day")
def advance_day(background_tasks: BackgroundTasks):
    """
    Advances the simulation by one full day.
    Triggers heavy background calculation of NPCs autonomously posting and reacting.
    Returns a potential Crucible Event or Offline Event.
    """
    def run_advance_day():
        engine.advance_day()
        save_state_to_db()

    background_tasks.add_task(run_advance_day)
    
    # Roll for a Crucible or Offline event
    daily_event = generate_daily_event()
    
    return {
        "status": "Day advancement triggered.",
        "day": engine.current_day + 1,
        "daily_event": daily_event
    }

class ResolveEventRequest(BaseModel):
    player_id: str
    event_id: str
    description: str # The description of the crisis
    response: str    # The player's written response or chosen option
    type: str        # "crisis", "opportunity", or "offline"
    risk_multiplier: float = 1.0

@app.post("/api/resolve_event")
def resolve_event(req: ResolveEventRequest):
    player = state.entities.get(req.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    if req.type == "offline":
        # For offline events, we just look at the selected option effect
        # This is a bit simplified for now
        if "Ignore" in req.response:
            player.aura = getattr(player, 'aura', 0) - 500
            return {"verdict": "You looked weak. The local neighborhood chat is laughing.", "aura_change": -500, "follower_change": 0}
        return {"verdict": "The situation was handled.", "aura_change": 0, "follower_change": 0}
    
    # For Twitter crises/opportunities
    result = engine.evaluate_crisis_response(player, req.description, req.response, req.risk_multiplier)
    return result

@app.post("/api/call_favor")
def call_favor(titan_id: str, player_id: str = "player_1"):
    player = state.entities.get(player_id)
    titan = state.entities.get(titan_id)
    if not player or not titan:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    score = getattr(player, 'alliance_scores', {}).get(titan_id, 0)
    if score < 80:
        return {"status": "error", "message": f"{titan.name} left you on read. (Alliance Score {score}/80 required)"}
        
    # Trigger a quote tweet from the Titan
    # Get last player post
    player_posts = [ev for ev in state.events if ev.initiator_id == player_id and ev.type == "tweet"]
    if not player_posts:
        return {"status": "error", "message": "Nothing for them to retweet."}
        
    last_post = player_posts[-1]
    
    # Force the Titan to interact
    import uuid
    retweet_event = Event(
        id=str(uuid.uuid4()),
        type="reply",
        content=f"Finally, someone gets it. @{player_id} is spitting facts.",
        initiator_id=titan_id,
        reply_to_id=last_post.id
    )
    engine.process_action(retweet_event)
    
    return {"status": "success", "message": f"{titan.name} just quote-replied to your post! Your notifications are exploding."}

@app.get("/api/vanguard")
def get_leaderboard():
    """
    Returns the top 100 entities ranked by Aura and Followers.
    """
    all_entities = list(state.entities.values())
    sorted_global = sorted(all_entities, key=lambda x: (x.follower_count, x.aura), reverse=True)
    leaderboard = []
    for i, e in enumerate(sorted_global[:100]):
        leaderboard.append({
            "handle": e.id,
            "name": e.name,
            "aura": e.aura,
            "followers": e.follower_count,
            "rank": i + 1,
            "faction": e.faction_tags[0] if e.faction_tags else "Neutral",
            "niche": e.primary_niche
        })
    return {"leaderboard": leaderboard}

@app.get("/api/leaderboards")
async def get_leaderboards(player_handle: str = "player_1"):
    player = state.entities.get(player_handle)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Sort everyone by Followers (Primary) and Aura (Secondary)
    all_entities = list(state.entities.values())
    sorted_global = sorted(all_entities, key=lambda x: (x.follower_count, x.aura), reverse=True)
    
    # Filter for the player's specific niche
    niche_entities = [e for e in sorted_global if e.primary_niche == player.primary_niche]
    
    # Find player indices (1-based rank)
    player_global_rank = 0
    player_niche_rank = 0
    
    for i, e in enumerate(sorted_global):
        if e.id == player_handle:
            player_global_rank = i + 1
            break
            
    for i, e in enumerate(niche_entities):
        if e.id == player_handle:
            player_niche_rank = i + 1
            break
    
    return {
        "global_vanguard": [
            {
                "id": e.id,
                "name": e.name, 
                "followers": e.follower_count, 
                "aura": e.aura,
                "rank": i + 1,
                "niche": e.primary_niche
            } 
            for i, e in enumerate(sorted_global[:100])
        ],
        "niche_kings": [
            {
                "id": e.id,
                "name": e.name, 
                "followers": e.follower_count, 
                "aura": e.aura,
                "rank": i + 1,
                "niche": e.primary_niche
            } 
            for i, e in enumerate(niche_entities[:50])
        ],
        "player_global_rank": player_global_rank,
        "player_niche_rank": player_niche_rank,
        "player_niche": player.primary_niche
    }

class MarketBuyRequest(BaseModel):
    player_id: str = "player_1"
    item_id: str # 'bot_net', 'engagement_pod', 'smear_campaign'
    target_id: Optional[str] = None # for smear_campaign

@app.post("/api/market/buy")
def shadow_market_buy(req: MarketBuyRequest):
    player = state.entities.get(req.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    items = {
        "bot_net": {"cost": 500, "followers": 5000, "heat": 20, "aura": -100},
        "engagement_pod": {"cost": 300, "heat": 10, "aura": -50},
        "smear_campaign": {"cost": 1000, "heat": 30},
        "premium_avatar": {"cost": 50000, "heat": 0, "aura": 100}
    }
    
    item = items.get(req.item_id)
    if not item:
        raise HTTPException(status_code=400, detail="Invalid item")
        
    cost = calculate_market_cost(req.item_id, player.follower_count)
    
    if player.wealth < cost:
        return {"status": "error", "message": f"Insufficient Wealth. You need {cost} Wealth to afford this."}
        
    player.wealth -= cost
    player.heat = min(100, player.heat + item["heat"])
    player.aura += item.get("aura", 0)
    
    if req.item_id == "premium_avatar":
        player.unlocked_premium_avatars = True
        # DiceBear 'notionists' style for premium look
        player.profile_image_url = f"https://api.dicebear.com/7.x/notionists/svg?seed={player.id}"
        
    if req.item_id == "bot_net":
        player.follower_count += item["followers"]
        player.recent_synthetic_growth += item["followers"]
        player.aura += item["aura"]
        return {"status": "success", "message": f"Bot Net deployed. {item['followers']} followers added. Heat is rising."}
        
    if req.item_id == "engagement_pod":
        player.aura += item["aura"]
        return {"status": "success", "message": "Engagement Pod active. Your next post will be prioritized by the swarm."}
        
    if req.item_id == "smear_campaign" and req.target_id:
        target = state.entities.get(req.target_id)
        if target:
            target.aura -= 1000
            return {"status": "success", "message": f"Smear campaign against {target.name} launched successfully."}
            
    return {"status": "success", "message": "Transaction complete."}

@app.post("/api/monetize")
def accept_promoted_post(player_id: str = "player_1"):
    player = state.entities.get(player_id)
    if not player: raise HTTPException(status_code=404)
    # Phase 24.1: Reward scales with organic engagement (E), boosted by momentum
    engagement = calculate_organic_engagement(
        player.follower_count, 
        player.aura, 
        momentum_buff=(player.momentum_buff_days > 0)
    )
    reward = calculate_monetization_reward(engagement)
    
    # Phase 24.3: Niche King Bonus (Rank #1 in niche = 2x Wealth)
    niche_entities = [e for e in state.entities.values() if e.primary_niche == player.primary_niche]
    sorted_niche = sorted(niche_entities, key=lambda x: x.follower_count, reverse=True)
    if sorted_niche and sorted_niche[0].id == player.id:
        reward *= 2
        print(f"[NICHE KING] @{player.id} is the King of {player.primary_niche}. Reward doubled to {reward}")
    
    player.wealth += reward
    player.aura -= 150 # Fixed reputation hit for selling out
    return {"status": "success", "wealth": player.wealth, "aura": player.aura, "message": f"Promoted post published. You earned {reward} Wealth."}

@app.get("/api/messages")
def get_messages(entity_id: str):
    """
    Returns all Private DMs targeted at the specified entity.
    """
    entity = state.entities.get(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    dms = []
    for ev in state.events:
        if ev.visibility == "Private" and ev.type == "dm" and entity_id in ev.target_ids:
            initiator = state.entities.get(ev.initiator_id)
            name = initiator.name if initiator else ev.initiator_id
            
            # Simple heuristic to flag hate speech in UI
            is_hate = False
            if "stupid" in ev.content.lower() or "hate" in ev.content.lower() or "idiot" in ev.content.lower() or "dumb" in ev.content.lower() or "worst" in ev.content.lower():
                is_hate = True
                
            dms.append({
                "id": ev.id,
                "from_handle": name.replace(" ", "_").lower(),
                "content": ev.content,
                "timestamp": ev.timestamp,
                "is_hate": is_hate
            })
            
    dms.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"messages": dms}

@app.get("/api/profile/{handle}")
def get_profile(handle: str):
    entity = state.entities.get(handle)
    if not entity:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_posts = [ev for ev in state.events if ev.initiator_id == handle]
    user_posts.sort(key=lambda x: x.timestamp, reverse=True)
    
    traits_preview = [{"trait": k.replace("_", " "), "value": v} for k, v in entity.public_vibe.items()]
    traits_preview.sort(key=lambda x: abs(x["value"]), reverse=True)
    traits_preview = traits_preview[:10]

    return {
        "name": entity.name,
        "handle": entity.id,
        "bio": entity.bio,
        "profile_image_url": entity.profile_image_url,
        "followers": entity.follower_count,
        "public_vibe": entity.public_vibe,
        "traits_preview": traits_preview,
        "recent_posts": [
            {
                "id": p.id, "content": p.content, "timestamp": p.timestamp, 
                "replies_count": p.replies_count, "likes_count": len(p.likes), 
                "retweets_count": len(p.retweets),
                "initiator_aura": entity.aura,
                "initiator_aura_debt": entity.aura_debt_posts
            } 
            for p in user_posts[:10]
        ],
        "is_verified": "Celebrity" in entity.faction_tags or "Verified" in entity.faction_tags,
        "ratio_count": sum(entity.ratio_tracker.values()) if entity.ratio_tracker else 0,
        "grudges_count": len(entity.long_term_memory.grudges) if entity.long_term_memory.grudges else 0,
        "rising_star_progress": int(min(100, (entity.follower_count / 10000.0) * 100)),
        "rivalries": getattr(entity, 'rivalries', [])
    }

class SettingsRequest(BaseModel):
    description: str

@app.post("/api/settings")
def update_settings(req: SettingsRequest):
    bio, top_traits = engine.initialize_identity_from_description(req.description)
    player = state.entities.get("player_1")
    if player:
        player.private_description = req.description
        player.bio = bio
        player.internal_truth.update(top_traits)
        # Update public vibe to reflect their true identity immediately for testing
        player.public_vibe.update(top_traits)
    return {"status": "success", "bio": bio, "top_traits": top_traits}

@app.post("/api/post_tweet")
def post_tweet(req: PostTweetRequest, background_tasks: BackgroundTasks):
    """
    Process a new post and run the engine loop.
    NEW: Includes deplatforming checks, auto-replies, and tier progression.
    """
    # Get player entity
    player = state.entities.get(req.initiator_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # PHASE 27: Check deplatforming condition before posting
    if engine.check_deplatform_condition(player):
        reason = "Toxicity Fatigue reached 100%" if player.toxicity_fatigue >= 100 else "Failed 3 Crucibles"
        deplatform_event = engine.trigger_deplatforming(player, reason)
        return {
            "status": "deplatformed",
            "reason": reason,
            "legacy_bonus_aura": player.legacy_aura_bonus,
            "legacy_bonus_wealth": player.generational_wealth
        }
    
    # 1. Analyze the hidden vibe / metadata of the tweet before processing
    impact_vectors = engine.analyze_tweet_vibe(req.content)
    
    event_type = "reply" if req.reply_to_id else ("tweet" if req.visibility == "Public" else "dm")
    new_event = Event(
        id=str(uuid.uuid4()),
        type=event_type,
        content=req.content,
        initiator_id=req.initiator_id,
        visibility=req.visibility,
        target_ids=req.target_ids,
        impact_vectors=impact_vectors,
        reply_to_id=req.reply_to_id,
        media_url=req.media_url,
        timestamp=time.time()
    )
    engine.process_action(new_event)
    
    # PHASE 27: Tier progression check
    from gamification import check_tier_progression
    check_tier_progression(player)
    
    # PHASE 27: Simulate daily NPC evolution (happens on post)
    engine.simulate_daily_npc_evolution()
    
    # Phase 23: Update alliance score if this is a DM to a Titan
    if event_type == "dm" and req.target_ids:
        if player:
            for tid in req.target_ids:
                engine.update_alliance_score(player, tid, req.content)

    # PHASE 27: Generate auto-replies from haters/lovers based on relationships
    async def generate_auto_replies_task(trigger_event):
        auto_reply_events = engine.generate_auto_replies(trigger_event, player)
        for auto_reply in auto_reply_events:
            engine.process_action(auto_reply)
            print(f"[AUTO-REPLY] {state.entities[auto_reply.initiator_id].name} auto-replied to {player.name}")
    
    # Trigger LLM responses from NPCs based on the new event
    # We run this in a background task so the frontend UI doesn't hang waiting for the LLM API to return
    async def trigger_ai_reactions(trigger_event):
        for npc_id, npc in state.entities.items():
            if npc_id != trigger_event.initiator_id and not npc.is_player:
                
                # Critical Fix: Only generate a reaction if the NPC actually "saw" the tweet in their visibility tier
                visible = engine.filter_events_for_entity(npc_id, [trigger_event])
                if not visible:
                    continue
                    
                # Add Stagger Logic to perfectly mimic human typing speed and avoid 429
                delay = random.randint(2, 6)
                await asyncio.sleep(delay)
                reaction = engine.generate_npc_reaction(npc_id, trigger_event)
                if reaction:
                    engine.process_action(reaction)
    
    # Run both auto-replies and AI reactions
    background_tasks.add_task(generate_auto_replies_task, new_event)
    background_tasks.add_task(trigger_ai_reactions, new_event)
    
    # Randomly step game logic
    engine.trigger_global_event_injector()
    
    return {
        "status": "success",
        "event_id": new_event.id,
        "tier_progress": getattr(player, 'tier_progress', 0),
        "account_tier": getattr(player, 'account_tier', 'guest')
    }
    
@app.get("/api/prompt/{entity_id}")
def get_prompt(entity_id: str):
    """
    Debug route to see what prompt the LLM will get for an entity.
    """
    return {"prompt": engine.generate_llm_prompt_for_entity(entity_id)}

@app.post("/api/heartbeat")
def receive_heartbeat(background_tasks: BackgroundTasks):
    """
    Next.js calls this every 30-60s. If called, there's a chance a World Pulse triggers.
    """
    # Phase 22: Save state periodically in the background
    background_tasks.add_task(save_state_to_db)
    
    # Phase 22: Gamification Check
    player = state.entities.get("player_1")
    quest_data = []
    if player:
        check_achievements(player)
        player.influence_rank = calculate_influence_rank(player)
        quest_data = DAILY_QUESTS
    
    if random.random() < 0.30: # 30% chance to trigger an autonomous NPC thread
        def run_pulse():
            engine.trigger_world_pulse()
        background_tasks.add_task(run_pulse)
        return {
            "status": "alive", 
            "pulse_triggered": True, 
            "quests": quest_data, 
            "achievements": getattr(player, "unlocked_achievements", []) if player else [],
            "player_wealth": getattr(player, "wealth", 0) if player else 0,
            "player_heat": getattr(player, "heat", 0) if player else 0,
            "player_aura_peak": getattr(player, "aura_peak", 1500) if player else 1500,
            "player_toxicity_fatigue": getattr(player, "toxicity_fatigue", 0) if player else 0,
            "player_stans": getattr(player, "stan_count", 0) if player else 0,
            "player_neutrals": getattr(player, "neutral_count", 0) if player else 0,
            "player_haters": getattr(player, "hater_count", 0) if player else 0,
            "player_aura_debt": getattr(player, "aura_debt_posts", 0) if player else 0,
            "is_griefing_account": getattr(player, "is_griefing_account", False) if player else False,
            "unlocked_premium_avatars": getattr(player, "unlocked_premium_avatars", False) if player else False,
            "chaos_mode_enabled": chaos_mode_enabled,
            "simulation_era": engine.simulation_era,
            "monthly_income_breakdown": getattr(player, "monthly_income_breakdown", {}) if player else {}
        }
        
    return {
        "status": "alive", 
        "pulse_triggered": False, 
        "quests": quest_data, 
        "influence_rank": getattr(player, "influence_rank", 1) if player else 1,
        "achievements": getattr(player, "unlocked_achievements", []) if player else [],
        "player_wealth": getattr(player, "wealth", 0) if player else 0,
        "player_heat": getattr(player, "heat", 0) if player else 0,
        "player_aura_peak": getattr(player, "aura_peak", 1500) if player else 1500,
        "player_toxicity_fatigue": getattr(player, "toxicity_fatigue", 0) if player else 0,
        "player_stans": getattr(player, "stan_count", 0) if player else 0,
        "player_neutrals": getattr(player, "neutral_count", 0) if player else 0,
        "player_haters": getattr(player, "hater_count", 0) if player else 0,
        "player_aura_debt": getattr(player, "aura_debt_posts", 0) if player else 0,
        "is_griefing_account": getattr(player, "is_griefing_account", False) if player else False,
        "unlocked_premium_avatars": getattr(player, "unlocked_premium_avatars", False) if player else False,
        "chaos_mode_enabled": chaos_mode_enabled,
        "simulation_era": engine.simulation_era,
        "monthly_income_breakdown": getattr(player, "monthly_income_breakdown", {}) if player else {}
    }

@app.post("/api/chaos/toggle")
def toggle_chaos_mode(enabled: bool):
    global chaos_mode_enabled
    chaos_mode_enabled = enabled
    print(f"[CHAOS] Toggle: {'ON' if chaos_mode_enabled else 'OFF'}")
    return {"status": "success", "chaos_mode_enabled": chaos_mode_enabled}

@app.get("/api/active_pulse")
def get_active_pulse():
    """
    Returns the currently active World Pulse (titans posting about trending topics).
    """
    return {"active_pulse": engine.active_pulse}

# --- Phase 19: Infrastructure Monitoring ---

@app.get("/api/rate_stats")
def get_rate_stats():
    """Returns current rate limiter statistics for monitoring API burn rate."""
    return engine.rate_limiter.get_stats()

# --- Phase 17: Neighborhood Hubs ---

@app.get("/api/neighborhood/{name}")
def get_neighborhood_feed(name: str):
    """
    Returns a filtered timeline showing only posts from NPCs
    tagged with the neighborhood's faction tags.
    """
    from visibility import filter_events_for_neighborhood
    from dictionaries import NEIGHBORHOOD_HUBS
    
    hub = NEIGHBORHOOD_HUBS.get(name)
    if not hub:
        raise HTTPException(status_code=404, detail=f"Neighborhood '{name}' not found.")
    
    events = filter_events_for_neighborhood(name, state.entities, state.events)
    events.sort(key=lambda x: x.timestamp, reverse=True)
    
    feed = []
    for ev in events[:30]:
        initiator = state.entities.get(ev.initiator_id)
        name_str = initiator.name if initiator else ev.initiator_id
        archetype = initiator.archetype if initiator else ""
        feed.append({
            "id": ev.id,
            "type": ev.type,
            "content": ev.content,
            "initiator_id": ev.initiator_id,
            "initiator_name": name_str,
            "initiator_archetype": archetype,
            "is_verified": getattr(initiator, "is_verified", False),
            "visibility": ev.visibility,
            "timestamp": ev.timestamp,
            "likes_count": len(ev.likes),
            "retweets_count": len(ev.retweets)
        })
    
    return {"feed": feed, "hub_description": hub["description"]}

class NeighborhoodPostRequest(BaseModel):
    entity_id: str
    content: str
    neighborhood: str

@app.post("/api/post_neighborhood")
def post_to_neighborhood(req: NeighborhoodPostRequest, background_tasks: BackgroundTasks):
    """
    Posts a tweet in a neighborhood feed. If the player fails the vibe-check,
    they are flagged as an Outsider and all NPC replies get a hostility boost.
    """
    from visibility import check_outsider_status
    
    entity = state.entities.get(req.entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    outsider_result = check_outsider_status(entity, req.neighborhood)
    
    impact_vectors = engine.analyze_tweet_vibe(req.content)
    
    new_event = Event(
        id=str(uuid.uuid4()),
        type="tweet",
        content=req.content,
        initiator_id=req.entity_id,
        visibility="Public",
        impact_vectors=impact_vectors
    )
    engine.process_action(new_event)
    
    # If outsider, boost hostility on all incoming replies
    async def trigger_hostile_reactions(trigger_event, hostility_bonus):
        for npc_id, npc in state.entities.items():
            if npc_id != trigger_event.initiator_id and not npc.is_player:
                # Check if this NPC belongs to the neighborhood
                from dictionaries import NEIGHBORHOOD_HUBS
                hub = NEIGHBORHOOD_HUBS.get(req.neighborhood, {})
                allowed_tags = set(hub.get("allowed_tags", []))
                entity_tags = set(t.replace(" ", "_") for t in npc.faction_tags)
                if entity_tags & allowed_tags:
                    delay = random.randint(1, 4)
                    await asyncio.sleep(delay)
                    # Temporarily boost hostility for outsider detection
                    original_hostility = npc.trait_matrix.hostility
                    npc.trait_matrix.hostility = min(100, npc.trait_matrix.hostility + hostility_bonus)
                    reaction = engine.generate_npc_reaction(npc_id, trigger_event)
                    npc.trait_matrix.hostility = original_hostility  # Reset
                    if reaction:
                        engine.process_action(reaction)
    
    background_tasks.add_task(trigger_hostile_reactions, new_event, outsider_result["hostility_bonus"])
    
    return {
        "status": "success",
        "event_id": new_event.id,
        "outsider_check": outsider_result
    }

# --- Phase 16: Monetization APIs ---

@app.post("/api/monetize")
async def monetize_aura(payload: dict):
    player_id = payload.get("initiator_id", "player_1")
    player = state.entities.get(player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    if player.follower_count >= 500:
        player.follower_count -= 500
        player.credits += 50
        return {"status": "success", "credits": player.credits, "aura": player.follower_count}
    
    raise HTTPException(status_code=400, detail="Insufficient Aura (Need 500+)")

@app.post("/api/buy_bots")
async def buy_engagement_swarm(payload: dict):
    player_id = payload.get("initiator_id", "player_1")
    target_event_id = payload.get("event_id")
    player = state.entities.get(player_id)
    
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    if player.credits >= 100:
        player.credits -= 100
        success = engine.force_bot_engagement(target_event_id, count=5)
        if success:
            return {"status": "success", "credits": player.credits, "message": "Swarm deployed."}
        else:
            player.credits += 100
            raise HTTPException(status_code=404, detail="Target post not found")
            
    raise HTTPException(status_code=400, detail="Insufficient Credits (Need 100)")

class ForceTrendRequest(BaseModel):
    entity_id: str
    trait_name: str

@app.post("/api/force_trend")
def force_trend(req: ForceTrendRequest):
    """
    Spends 250 Credits to inject 50 fake events mapping to a specific trait to manipulate the algorithm.
    """
    entity = state.entities.get(req.entity_id)
    if not entity or entity.simulated_credits < 250:
        return HTTPException(status_code=400, detail="Not enough credits or entity not found.")
        
    entity.simulated_credits -= 250
    
    import uuid
    import time
    for _ in range(50):
        fake_event = Event(
            id=str(uuid.uuid4()),
            type="tweet",
            content="[BOTTED ENGAGEMENT]",
            initiator_id="SYSTEM",
            visibility="Private", # Keep it off the timeline
            timestamp=time.time(),
            impact_vectors={req.trait_name: 100}
        )
        state.events.append(fake_event)
        
    return {"status": "success", "new_credits": entity.simulated_credits, "message": f"{req.trait_name} artificially boosted."}

# --- Phase 21: God Mode Admin Panel ---

@app.post("/api/admin/force_pulse")
def admin_force_pulse():
    """God Mode: Manually triggers a World Pulse event."""
    engine.trigger_global_event_injector()
    return {"status": "success", "message": "World Pulse injected.", "active_pulse": engine.active_pulse}

class InjectScandalRequest(BaseModel):
    target_id: str
    scandal_text: str

@app.post("/api/admin/inject_scandal")
def admin_inject_scandal(req: InjectScandalRequest, background_tasks: BackgroundTasks):
    """God Mode: Injects a manufactured scandal targeting a specific NPC or player."""
    target = state.entities.get(req.target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Entity not found.")
    
    import time
    scandal_event = Event(
        id=str(uuid.uuid4()),
        type="news",
        content=f"🚨 BREAKING SCANDAL: {target.name} exposed — {req.scandal_text}",
        initiator_id="SYSTEM",
        visibility="Public",
        timestamp=time.time(),
        impact_vectors={}
    )
    engine.process_action(scandal_event)
    
    # Trigger hostile reactions from the swarm
    swarm_bots = [e for e in state.entities.values() if not e.is_player and "Celebrity" not in e.faction_tags]
    random.shuffle(swarm_bots)
    
    def _scandal_reactions():
        for bot in swarm_bots[:8]:
            reaction = engine.generate_npc_reaction(bot.id, scandal_event)
            if reaction:
                engine.process_action(reaction)
    
    background_tasks.add_task(_scandal_reactions)
    
    engine.active_pulse = {
        "topic": f"SCANDAL: {target.name}",
        "initiator_name": "GOD MODE",
        "timestamp": time.time()
    }
    
    return {"status": "success", "message": f"Scandal injected against {target.name}."}

class EditTraitsRequest(BaseModel):
    entity_id: str
    traits: dict  # {trait_name: score (-100 to 100)}

@app.post("/api/admin/edit_traits")
def admin_edit_traits(req: EditTraitsRequest):
    """God Mode: Manually edits an NPC's internal truth vector."""
    entity = state.entities.get(req.entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found.")
    
    changes_made = []
    for trait, score in req.traits.items():
        clamped = max(-100, min(100, int(score)))
        old_val = entity.internal_truth.get(trait, 0)
        entity.internal_truth[trait] = clamped
        changes_made.append({"trait": trait, "old": old_val, "new": clamped})
    
    return {"status": "success", "entity": entity.name, "changes": changes_made}

@app.get("/api/admin/entities")
def admin_list_entities():
    """God Mode: Returns full roster of all entities with their stats."""
    roster = []
    for eid, e in state.entities.items():
        top_traits = sorted(e.internal_truth.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        roster.append({
            "id": eid,
            "name": e.name,
            "archetype": e.archetype,
            "faction_tags": e.faction_tags,
            "follower_count": e.follower_count,
            "is_verified": e.is_verified,
            "is_player": e.is_player,
            "is_rising_star": e.is_rising_star,
            "total_engagement": e.total_engagement,
            "grudges": e.long_term_memory.grudges,
            "top_traits": {k: v for k, v in top_traits},
            "hostility": e.trait_matrix.hostility
        })
    return {"entities": roster, "total_count": len(roster)}

@app.get("/api/admin/export_state")
def admin_export_state():
    """
    God Mode: Exports the full 'State of the City' report.
    Shows ideological landscape shifts, faction populations, vibe heatmap, and entity arcs.
    """
    from collections import defaultdict
    import time
    
    # 1. Global Ideology Heatmap
    trait_totals = defaultdict(lambda: {"sum": 0, "count": 0, "extremes": 0})
    faction_counts = defaultdict(int)
    archetype_counts = defaultdict(int)
    
    rising_stars = []
    grudge_holders = []
    verified_count = 0
    
    for eid, e in state.entities.items():
        if e.is_player:
            continue
        
        # Aggregate traits
        for trait, score in e.internal_truth.items():
            trait_totals[trait]["sum"] += score
            trait_totals[trait]["count"] += 1
            if abs(score) > 75:
                trait_totals[trait]["extremes"] += 1
        
        # Faction counts
        for tag in e.faction_tags:
            faction_counts[tag] += 1
        
        # Archetype counts
        archetype_counts[e.archetype] += 1
        
        # Rising stars
        if e.is_rising_star and e.archetype != "The Swarm":
            rising_stars.append({"name": e.name, "archetype": e.archetype, "followers": e.follower_count, "engagement": e.total_engagement})
        
        # Grudge holders
        if e.long_term_memory.grudges:
            grudge_holders.append({"name": e.name, "grudges_against": e.long_term_memory.grudges})
        
        if e.is_verified:
            verified_count += 1
    
    # 2. Ideological Averages
    ideology_report = {}
    for trait, data in sorted(trait_totals.items(), key=lambda x: x[1]["count"], reverse=True)[:20]:
        avg = data["sum"] / data["count"] if data["count"] > 0 else 0
        ideology_report[trait] = {
            "average_score": round(avg, 1),
            "total_npcs_with_opinion": data["count"],
            "extremists": data["extremes"],
            "lean": "Left/Negative" if avg < -25 else "Right/Positive" if avg > 25 else "Centrist/Neutral"
        }
    
    # 3. Trending history
    trending = engine.get_trending_topics()
    
    # 4. Player stats
    player = state.entities.get("player_1")
    player_report = {}
    if player:
        player_report = {
            "aura": player.follower_count,
            "credits": player.simulated_credits,
            "top_public_vibes": sorted(player.public_vibe.items(), key=lambda x: abs(x[1]), reverse=True)[:10],
            "total_posts": len([e for e in state.events if e.initiator_id == "player_1"]),
        }
    
    # 5. Rate limiter stats
    rate_stats = engine.rate_limiter.get_stats()
    
    return {
        "report_title": "TwitLife: State of the City",
        "generated_at": time.time(),
        "total_entities": len(state.entities),
        "total_events": len(state.events),
        "verified_accounts": verified_count,
        "ideology_landscape": ideology_report,
        "faction_populations": dict(faction_counts),
        "archetype_breakdown": dict(archetype_counts),
        "trending_topics": trending,
        "rising_star_arcs": rising_stars,
        "grudge_network": grudge_holders,
        "player_report": player_report,
        "api_usage": rate_stats
    }

# --- PHASE 27: World Events & God Mode (BitLife Systems) ---

class WorldEventRequest(BaseModel):
    player_id: str = "player_1"
    event_type: str  # "hater_winter" or "algorithm_shift"

@app.post("/api/world_events/trigger")
def trigger_world_event(req: WorldEventRequest):
    """
    Triggers a world event that affects all NPCs.
    - hater_winter: 7-day period where NPCs are 50% more hostile
    - algorithm_shift: Randomize which topics get algorithmic boost/shadowban
    """
    player = state.entities.get(req.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if req.event_type == "hater_winter":
        success = engine.trigger_hater_winter(duration_days=7)
        if success:
            return {
                "status": "success",
                "event": "hater_winter",
                "message": "❄️ HATER WINTER BEGINS! The entire network becomes 50% more hostile for 7 days.",
                "active_world_events": engine.active_world_events
            }
        else:
            return {
                "status": "error",
                "message": "Hater Winter is already active or RNG didn't trigger."
            }
    
    elif req.event_type == "algorithm_shift":
        winners, losers = engine.trigger_algorithmic_shift()
        return {
            "status": "success",
            "event": "algorithm_shift",
            "message": "🔀 ALGORITHM SHIFTED! Topic reach multipliers have been randomized.",
            "winners": winners,
            "losers": losers,
            "active_world_events": engine.active_world_events
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unknown event type")

@app.get("/api/world_state")
def get_world_state():
    """
    Returns active world events and their modifiers.
    """
    player = state.entities.get("player_1")
    
    hater_winter_status = {
        "active": engine.hater_winter_active,
        "days_remaining": max(0, engine.hater_winter_end_day - engine.current_day) if engine.hater_winter_active else 0,
        "heat_multiplier": engine.get_hater_winter_heat_multiplier()
    }
    
    algo_shifts = {
        "active": len(engine.algorithmic_topic_multipliers) > 0,
        "topic_multipliers": engine.algorithmic_topic_multipliers
    }
    
    return {
        "status": "success",
        "current_day": engine.current_day,
        "simulation_era": engine.simulation_era,
        "world_events": {
            "hater_winter": hater_winter_status,
            "algorithm_shift": algo_shifts
        },
        "player_stats": {
            "aura": getattr(player, 'aura', 0) if player else 0,
            "wealth": getattr(player, 'wealth', 0) if player else 0,
            "heat": getattr(player, 'heat', 0) if player else 0,
            "toxicity_fatigue": getattr(player, 'toxicity_fatigue', 0) if player else 0
        }
    }

# --- God Mode: Propaganda Machine & Psychological Warfare ---

class GodModeActionRequest(BaseModel):
    player_id: str = "player_1"
    action_type: str  # "propaganda_machine", "reveal_truth", "edit_truth", "leak_dm"
    target_id: str = None
    custom_message: str = None
    belief_key: str = None
    old_word: str = None
    new_word: str = None

@app.post("/api/god_mode/action")
def god_mode_action(req: GodModeActionRequest):
    """
    Execute god mode actions that cost Aura and have lasting consequences.
    - propaganda_machine: 50 Wealth; Force NPC to post custom message for 24h
    - reveal_truth: 100 Aura; View NPC's internal beliefs and system prompt
    - edit_truth: 200 Aura; Permanently rewrite one belief by changing a word
    - leak_dm: 150 Aura; Trigger a Crucible event on target
    """
    player = state.entities.get(req.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    target = state.entities.get(req.target_id) if req.target_id else None
    
    # --- ACTION 1: Propaganda Machine (50 Wealth) ---
    if req.action_type == "propaganda_machine":
        if not target:
            raise HTTPException(status_code=404, detail="Target NPC not found")
        
        if player.wealth < 50:
            return {
                "status": "error",
                "message": f"Insufficient Wealth! Need 50, you have {player.wealth}",
                "cost": 50,
                "currency": "Wealth"
            }
        
        player.wealth -= 50
        result = engine.propaganda_machine(player, target.id, req.custom_message)
        
        if result:
            return {
                "status": "success",
                "action": "propaganda_machine",
                "cost_paid": 50,
                "message": f"✅ Propaganda machine deployed! {target.name} will post: '{req.custom_message}' for the next 24 hours.",
                "target_id": target.id,
                "target_name": target.name
            }
    
    # --- ACTION 2: Reveal Truth (100 Aura) ---
    elif req.action_type == "reveal_truth":
        if not target:
            raise HTTPException(status_code=404, detail="Target NPC not found")
        
        if player.aura < 100:
            return {
                "status": "error",
                "message": f"Insufficient Aura! Need 100, you have {player.aura}",
                "cost": 100,
                "currency": "Aura"
            }
        
        player.aura -= 100
        
        return {
            "status": "success",
            "action": "reveal_truth",
            "cost_paid": 100,
            "message": f"🔍 Internal truth of {target.name} revealed:",
            "target_name": target.name,
            "internal_truth": target.internal_truth,
            "system_prompt_hint": str(target.system_prompt_lock[:200]) + "..." if target.system_prompt_lock else "None",
            "faction_tags": target.faction_tags,
            "trait_matrix": {
                "hostility": target.trait_matrix.hostility,
                "politics": target.trait_matrix.politics,
                "tone": target.trait_matrix.tone
            }
        }
    
    # --- ACTION 3: Edit Truth (200 Aura) ---
    elif req.action_type == "edit_truth":
        if not target:
            raise HTTPException(status_code=404, detail="Target NPC not found")
        
        if player.aura < 200:
            return {
                "status": "error",
                "message": f"Insufficient Aura! Need 200, you have {player.aura}",
                "cost": 200,
                "currency": "Aura"
            }
        
        if not req.belief_key or not req.old_word or not req.new_word:
            raise HTTPException(status_code=400, detail="Must provide belief_key, old_word, new_word")
        
        player.aura -= 200
        
        # Edit the belief
        if req.belief_key in target.internal_truth:
            old_belief = target.internal_truth[req.belief_key]
            # Rewrite: replace old_word with new_word in the belief value
            if isinstance(old_belief, str):
                new_belief = old_belief.replace(req.old_word, req.new_word)
                target.internal_truth[req.belief_key] = new_belief
                
                return {
                    "status": "success",
                    "action": "edit_truth",
                    "cost_paid": 200,
                    "message": f"✏️ Rewrote {target.name}'s belief!",
                    "target_name": target.name,
                    "belief_key": req.belief_key,
                    "old_belief": old_belief,
                    "new_belief": new_belief
                }
            else:
                return {
                    "status": "error",
                    "message": f"Belief '{req.belief_key}' is not a string (type: {type(old_belief).__name__})"
                }
        else:
            return {
                "status": "error",
                "message": f"Belief key '{req.belief_key}' not found in {target.name}'s internal truth"
            }
    
    # --- ACTION 4: Leak DM (150 Aura) ---
    elif req.action_type == "leak_dm":
        if not target:
            raise HTTPException(status_code=404, detail="Target NPC not found")
        
        if player.aura < 150:
            return {
                "status": "error",
                "message": f"Insufficient Aura! Need 150, you have {player.aura}",
                "cost": 150,
                "currency": "Aura"
            }
        
        player.aura -= 150
        
        # Trigger a Crucible on the target (crisis decision moment)
        crisis_description = f"A leaked DM from you surfaced online:\n'{req.custom_message if req.custom_message else 'CLASSIFIED CONTENT'}'\n\nAll eyes on you now."
        
        import uuid
        crucible_event = Event(
            id=str(uuid.uuid4()),
            type="crucible",
            content=crisis_description,
            initiator_id="SYSTEM",
            visibility="Public",
            target_ids=[target.id]
        )
        engine.process_action(crucible_event)
        
        return {
            "status": "success",
            "action": "leak_dm",
            "cost_paid": 150,
            "message": f"💣 Leaked DM triggered a CRUCIBLE on {target.name}!",
            "target_name": target.name,
            "crucible_description": crisis_description
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unknown god mode action")

@app.post("/api/god_mode/propaganda_machine")
def god_mode_propaganda_machine(player_id: str, target_npc_id: str, custom_message: str):
    """
    Shorthand endpoint for propaganda machine action.
    Costs 50 Wealth; forces target NPC to post custom message for 24h.
    """
    req = GodModeActionRequest(
        player_id=player_id,
        action_type="propaganda_machine",
        target_id=target_npc_id,
        custom_message=custom_message
    )
    return god_mode_action(req)

@app.post("/api/god_mode/leak_dm")
def god_mode_leak_dm(player_id: str, target_npc_id: str, dm_text: str):
    """
    Shorthand endpoint for leak DM action.
    Costs 150 Aura; triggers a Crucible on target.
    """
    req = GodModeActionRequest(
        player_id=player_id,
        action_type="leak_dm",
        target_id=target_npc_id,
        custom_message=dm_text
    )
    return god_mode_action(req)

@app.post("/api/god_mode/edit_truth")
def god_mode_edit_truth(player_id: str, target_npc_id: str, belief_key: str, old_word: str, new_word: str):
    """
    Shorthand endpoint for edit truth action.
    Costs 200 Aura; permanently rewrites one NPC belief.
    """
    req = GodModeActionRequest(
        player_id=player_id,
        action_type="edit_truth",
        target_id=target_npc_id,
        belief_key=belief_key,
        old_word=old_word,
        new_word=new_word
    )
    return god_mode_action(req)

