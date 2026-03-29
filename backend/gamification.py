# backend/gamification.py

ACHIEVEMENTS = {
    "first_dogpile": {
        "name": "Cancelled", 
        "desc": "Survive your first mob rule", 
        "reward_credits": 500
    },
    "start_war": {
        "name": "Chaos Agent", 
        "desc": "Trigger 5 faction quote wars", 
        "reward_verifed_badge": True
    },
    "global_titan": {
        "name": "Local God", 
        "desc": "Reach 50k followers", 
        "reward_credits": 1000
    }
}

DAILY_QUESTS = [
    {"id": "quest_neighborhood", "desc": "Post 3 times in a neighborhood", "reward": 150},
    {"id": "quest_ratio", "desc": "Ratio a Titan", "reward": 300},
    {"id": "quest_note", "desc": "Get hit with a Community Note", "reward": 50}
]

def calculate_influence_rank(entity) -> int:
    """
    Calculates 1-100 influence rank based on followers, engagement, and faction wins.
    """
    base = entity.follower_count / 1000.0
    engagement_bonus = getattr(entity, 'total_engagement', 0) / 100.0
    
    raw_score = base + engagement_bonus
    # Scale it to 1-100 curve
    rank = int(min(100, max(1, (raw_score / 500) * 100)))
    return rank

def check_achievements(entity):
    """
    Evaluates current state against achievement unlock conditions.
    """
    unlocked = getattr(entity, 'unlocked_achievements', [])
    new_unlocks = []
    
    if "first_dogpile" not in unlocked and getattr(entity, 'is_dogpiled', False):
        new_unlocks.append("first_dogpile")
        entity.simulated_credits = getattr(entity, 'simulated_credits', 0) + 500
        
    if "global_titan" not in unlocked and entity.follower_count >= 50000:
        new_unlocks.append("global_titan")
        entity.simulated_credits = getattr(entity, 'simulated_credits', 0) + 1000
        
    if new_unlocks:
        entity.unlocked_achievements = list(set(unlocked + new_unlocks))
        
    return new_unlocks

import random

CRUCIBLE_EVENTS = [
    {
        "type": "crisis",
        "title": "🚨 DOCTORED DMs LEAKED",
        "template": "A highly followed {faction} bot just posted 'screenshots' of you aggressively insulting their community in a private DM. It's hitting the Trending sidebar. You have 10 minutes to respond before you lose the narrative.",
        "risk_multiplier": 2.0
    },
    {
        "type": "crisis",
        "title": "🚨 OLD TAKES RESURFACED",
        "template": "Someone just dug up a terrible, highly controversial take you had about {domain} from three years ago. The quote retweets are piling up.",
        "risk_multiplier": 1.5
    },
    {
        "type": "opportunity",
        "title": "🌟 TITAN ENDORSEMENT",
        "template": "Out of nowhere, {titan} just quote-tweeted your last post saying 'Finally, someone gets it.' Your notifications are melting. What's your follow-up?",
        "risk_multiplier": 1.5
    }
]

# ========== PHASE 27: ACCOUNT TIER PROGRESSION ==========

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
            "condition": lambda e: getattr(e, 'current_streak', 0) >= 10,
            "reward": 1
        },
        {
            "id": "survive_crucible",
            "desc": "Survive a Crucible without failure",
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
            "desc": "Build +50 relationship with 3 entities",
            "condition": lambda e: sum(1 for s in e.long_term_memory.relationship_matrix.values() if s >= 50) >= 3,
            "reward": 1
        }
    ]
}

def check_tier_progression(entity) -> int:
    """
    Returns progress (0-5) for verified tier. At 5/5, tier unlocked.
    Updates entity.account_tier if tier is earned.
    """
    from models import AccountTier
    
    if entity.account_tier != AccountTier.GUEST:
        return -1  # Already verified or higher
    
    tier_progress = getattr(entity, 'tier_progress', 0) or 0
    quests = TIER_PROGRESSION_QUESTS.get("verified", [])
    
    for quest in quests:
        if quest["condition"](entity) and quest["id"] not in getattr(entity, '_completed_tier_quests', []):
            tier_progress += quest["reward"]
            if not hasattr(entity, '_completed_tier_quests'):
                entity._completed_tier_quests = []
            entity._completed_tier_quests.append(quest["id"])
    
    entity.tier_progress = tier_progress
    
    if tier_progress >= 5:
        entity.account_tier = AccountTier.VERIFIED
        entity.is_shadowbanned = False
        entity.shadowban_until = 0.0
        print(f"[TIER UP] {entity.name} is now VERIFIED!")
        return 5
    
    return tier_progress

OFFLINE_EVENTS = [
    {
        "type": "offline",
        "title": "🏋️ GYM CONFRONTATION",
        "description": "A guy at your gym recognized you from your viral tweet arguing about the Art Museum steps. He looks angry and is walking toward you.",
        "options": [
            {"label": "Post a live thread about him", "effect": "clout_boost", "risk": "physical_penalty"},
            {"label": "Put your headphones in and ignore him", "effect": "aura_loss", "amount": -500},
            {"label": "Apologize", "effect": "sanity_drop"}
        ]
    }
]

def generate_daily_event(game_state=None):
    # 30% chance of a major event trigger on day advance
    if random.random() > 0.3:
        return None

    # Roll for Twitter vs Offline event
    if random.random() < 0.7:
        # Twitter Crucible Event
        event = random.choice(CRUCIBLE_EVENTS)
        
        # Dynamically inject (mocking state lookups for now, can refine later)
        faction = random.choice(["MAGA Titans", "Progressive Left", "Delco Trolls", "Fishtown Artists"])
        domain = random.choice(["politics", "philly_local", "pop_culture", "real_estate"])
        titan = random.choice(["@AOC", "@realDonaldTrump", "@taylorswift13", "@GrittyNHL", "@elonmusk"])
        
        desc = event["template"].format(faction=faction, domain=domain, titan=titan)
        
        return {
            "event_id": f"evt_{random.randint(1000, 9999)}",
            "title": event["title"],
            "description": desc,
            "type": event["type"],
            "risk_multiplier": event["risk_multiplier"]
        }
    else:
        # Offline Event
        event = random.choice(OFFLINE_EVENTS)
        return {
            "event_id": f"off_{random.randint(1000, 9999)}",
            "title": event["title"],
            "description": event["description"],
            "type": "offline",
            "options": event["options"]
        }

def calculate_vanguard_ranks(entities: dict):
    """
    Ranks all entities based on a composite score of Aura and Followers.
    Sets the vanguard_rank attribute on each entity.
    """
    scores = []
    for eid, entity in entities.items():
        aura = getattr(entity, 'aura', 1500)
        followers = entity.follower_count
        # Phase 24 check: Use log followers for more competitive ranking at the top
        composite = aura + (math.log10(followers + 1) * 1000)
        scores.append((eid, composite))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (eid, _) in enumerate(scores, 1):
        entities[eid].vanguard_rank = rank
        
    return scores[:100]

def calculate_market_cost(item_id: str, current_followers: int) -> int:
    """
    Phase 24: Dynamic Pricing Function
    Scaling C_base by (F/1000) factor to match "millions" requirement.
    """
    base_prices = {
        "bot_net": 500,
        "engagement_pod": 300,
        "smear_campaign": 1000,
        "premium_avatar": 50000
    }
    C_base = base_prices.get(item_id, 500)
    
    if item_id == "premium_avatar":
        return C_base # Flat price for vanity items
    
    # Scaling factor: base price * (1 + sqrt(F/100))
    # At 1k followers: 1 + 3.16 = 4.16. 500 * 4.16 = 2k.
    # At 1M followers: 1 + 100 = 101. 500 * 101 = 50.5k.
    # To reach millions at 1M followers, we need more.
    # Let's use (F/10)^0.6 scaling or similar.
    # At 1M: (100,000)^0.6 = 1000. 500 * 1000 = 500k.
    # At 10M: (1M)^0.6 = 4000. 500 * 4000 = 2M.
    
    multiplier = math.pow(max(10, current_followers) / 10.0, 0.6)
    return int(C_base * multiplier)

def calculate_monetization_reward(engagement: float) -> int:
    """
    ΔW = E * R_CPM
    R_CPM scaled for promoted posts.
    """
    R_CPM = 5.0 # Wealth per 1000 engagement units
    wealth = int(engagement * R_CPM)
    return max(100, wealth) # Minimum payout for selling out
