import random
from typing import Dict
from models import Entity

def process_supporter_conversion(entity: Entity, new_followers: int):
    """
    Called when an entity gains followers. 
    Each new follower has a probabilistic chance to convert into a paying supporter.
    """
    if new_followers <= 0:
        return
        
    t1_chance = 0.02
    t2_chance = 0.005
    t3_chance = 0.0005
    
    for _ in range(new_followers):
        roll = random.random()
        if roll < t3_chance:
            entity.t3_supporters += 1
        elif roll < t2_chance:
            entity.t2_supporters += 1
        elif roll < t1_chance:
            entity.t1_supporters += 1

def calculate_niche_income(entity: Entity) -> Dict[str, any]:
    """
    Calculates monthly income breakdown based on explicit supporter counts.
    Phase 27: Probabilistic Supporter Model.
    """
    niche = entity.primary_niche.lower()
    f = entity.follower_count
    
    # Base revenue from all followers ("Pocket Change")
    base_rev = int(f * 0.001)
    
    breakdown = {
        "monthly_total": 0,
        "segments": {},
        "currency": "Wealth"
    }
    
    # Niche-specific labels and values
    if niche == "streamer":
        t1_label, t1_val = "Tier 1 Subs", 5
        t2_label, t2_val = "Tier 2 Subs", 10
        t3_label, t3_val = "Tier 3 Subs", 25
        extra_label, extra_rev = "Bits & Donos", 0 # Calculated below
    elif niche == "tech":
        t1_label, t1_val = "SaaS Subs", 50
        t2_label, t2_val = "Consulting", 500
        t3_label, t3_val = "Deep Partners", 5000
        extra_label, extra_rev = "Sponsors", int(f * 0.10)
    elif niche == "artist":
        t1_label, t1_val = "Patrons", 10
        t2_label, t2_val = "Collectors", 100
        t3_label, t3_val = "Whales", 1000
        extra_label, extra_rev = "Commissions", int(f * 0.05)
    elif niche == "music":
        t1_label, t1_val = "Superfans", 10
        t2_label, t2_val = "VIPs", 50
        t3_label, t3_val = "Backers", 200
        extra_label, extra_rev = "Streams", int(f * 10 * 0.003)
    elif "combat" in niche or "sports" in niche:
        t1_label, t1_val = "PPV Points", 20
        t2_label, t2_val = "Gym Members", 100
        t3_label, t3_val = "Sponsors", 500
        extra_label, extra_rev = "Merch", int(f * 0.05)
    else:
        t1_label, t1_val = "Supporters", 1
        t2_label, t2_val = "Fans", 5
        t3_label, t3_val = "Stans", 20
        extra_label, extra_rev = "Ad Revenue", int(f * 0.01)

    t1_rev = entity.t1_supporters * t1_val
    t2_rev = entity.t2_supporters * t2_val
    t3_rev = entity.t3_supporters * t3_val
    
    if niche == "streamer":
        extra_rev = int((t1_rev + t2_rev + t3_rev) * 0.67)

    breakdown["segments"] = {
        t1_label: entity.t1_supporters if niche != "general" else t1_rev,
        t2_label: entity.t2_supporters if niche != "general" else t2_rev,
        t3_label: entity.t3_supporters if niche != "general" else t3_rev,
        extra_label: extra_rev,
        "Base Reach": base_rev
    }
    
    breakdown["monthly_total"] = t1_rev + t2_rev + t3_rev + extra_rev + base_rev
    
    return breakdown
