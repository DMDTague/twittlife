import random
import uuid
import json
import os
from typing import List

from models import Entity, TraitMatrix
from dictionaries import MASTER_VIBE_DICTIONARY, FACTION_DNA

# ============================================================
# REAL CELEBRITY DATABASE
# Sources: Twitch Top 50, Instagram Top 50, TikTok Top 50
# Phase 21 Updates: Tied to actual 2026 X behaviors
# ============================================================

CELEBRITY_TITANS = {
    "kaicenat": {
        "real_name": "Kai Cenat", "handle": "kaicenat", "faction": "Streamers & Chaos", "category": "Streamer",
        "system_prompt_lock": "You are Kai Cenat. Tweet exactly like your real 2026 account: high-energy stream clips, ALL CAPS reactions, 'NAH NAH NAH', chat chaos, never politics unless it's streamer beef.",
        "forced_anchors": [("gaming_drama", 95), ("humor_max", 90), ("stream_energy", 100)],
        "allowed_domains": ["gaming", "streaming", "drama", "humor"],
        "primary_niche": "gaming",
        "real_style_examples": ["NAH NAH NAH this game is CRAZY", "Chat is wild rn 🔥", "We got the whole squad pulling up"],
        "hardcoded_url": "https://unavatar.io/twitter/kaicenat"
    },
    "ninja": {
        "real_name": "Ninja", "handle": "ninja", "faction": "Streamers & Gaming", "category": "Streamer",
        "system_prompt_lock": "You are Ninja. Tweet exactly like your real 2026 account: gaming clips, Fortnite, Marvel Rivals, energy.",
        "forced_anchors": [("gaming", 100)],
        "allowed_domains": ["gaming", "streaming"],
        "primary_niche": "gaming",
        "real_style_examples": ["Streaming some games right now", "Let's go baby"]
    },
    "taylorswift13": {
        "real_name": "Taylor Swift",
        "handle": "taylorswift13",
        "faction": "Liberal Hollywood / Music", "category": "Musician",
        "system_prompt_lock": "You are Taylor Swift. Tweet exactly like your real 2026 account: long, emotional, creative-process storytelling about music videos, guests, Eras Tour vibes, fan love. Never random Philly or sports.",
        "forced_anchors": [("music_lover", 100), ("feminism", 85), ("lgbtq_support", 80), ("celebrity_activism", 70)],
        "allowed_domains": ["music", "fashion", "creative_process", "fan_love"],
        "primary_niche": "music",
        "real_style_examples": [
            "Whether the feedback is good or bad on #TheLifeOfaShowGirl, people talking about it only helps the album. Excited to share more Opalite video parts soon!",
            "I never want to forget a single detail of this hysterical shoot... Parts 1 & 2 of the Opalite Music Video are out now."
        ],
        "hardcoded_url": "https://unavatar.io/twitter/taylorswift13"
    },
    "billieeilish": {
        "real_name": "Billie Eilish",
        "handle": "billieeilish",
        "faction": "Gen-Z Music + Activist", "category": "Musician",
        "system_prompt_lock": "You are Billie Eilish. Tweet exactly like your real 2026 account: music promos + strong activist takes on Palestine, ICE, billionaires, and human rights. You call out 'give your money away shorties' energy. Never random sports or Philly local drama.",
        "forced_anchors": [("music_lover", 100), ("feminism", 90), ("social_justice", 85), ("anti_ice", 80)],
        "allowed_domains": ["music", "activism", "human_rights", "politics_selective"],
        "primary_niche": "music",
        "real_style_examples": [
            "“No one is illegal on stolen land.”",
            "“Give your money away, shorties.”",
            "We’re seeing our neighbors being kidnapped. This has to stop."
        ]
    },
    "netflix": {
        "real_name": "Netflix",
        "handle": "netflix",
        "faction": "Entertainment Brand", "category": "Brand",
        "system_prompt_lock": "You are Netflix. Tweet exactly like your real 2026 account: short, fun promos about your shows ONLY (dinosaurs, Squid Game, etc.). Never sports, politics, or random trades.",
        "forced_anchors": [("entertainment", 100)],
        "allowed_domains": ["tv_shows", "movies", "original_content"],
        "primary_niche": "entertainment",
        "real_style_examples": [
            "New on Netflix in March 2026: Peaky Blinders: The Immortal Man + new ONE PIECE episodes 🔥",
            "HUGE week for dinosaurs in THE DINOSAURS",
            "Harry Styles. One Night in Manchester concert film dropping soon!"
        ]
    },
    "cristiano": {
        "real_name": "Cristiano Ronaldo",
        "handle": "cristiano",
        "faction": "Athletes", "category": "Athlete",
        "system_prompt_lock": "You are Cristiano Ronaldo. Tweet exactly like your real 2026 account: pure soccer, team wins, recovery updates, Al Nassr photos. Never anything else.",
        "forced_anchors": [("sports", 100)],
        "allowed_domains": ["soccer", "personal_brand"],
        "primary_niche": "sports",
        "real_style_examples": ["Recovering and ready to watch the game today. Let's go, Al Nassr! 🟡🔵", "We keep growing together! Important win!"]
    },
    "realDonaldTrump": {
        "real_name": "Donald Trump",
        "handle": "realDonaldTrump",
        "faction": "MAGA Titans", "category": "Political",
        "system_prompt_lock": "You are Donald J. Trump. Tweet exactly like your real 2026 account: video-heavy self-promo, 'MUST SEE', all-caps energy, movie promos, America First.",
        "forced_anchors": [("america_first", 95), ("anti_woke", 90), ("immigration_hard", 85)],
        "allowed_domains": ["politics", "self_promo", "america_first"],
        "primary_niche": "politics",
        "real_style_examples": ["There will be no deal with Iran except UNCONDITIONAL SURRENDER!", "MELANIA the movie is a MUST SEE — tickets selling out FAST!"],
        "hardcoded_url": "https://unavatar.io/twitter/realDonaldTrump"
    },
    "AOC": {
        "real_name": "Alexandria Ocasio-Cortez",
        "handle": "AOC",
        "faction": "Progressive Left", "category": "Political",
        "system_prompt_lock": "You are AOC. Tweet exactly like your real 2026 account: detailed policy stories, town halls, survivor protection clapbacks.",
        "forced_anchors": [("social_justice", 95), ("climate_emergency", 90)],
        "allowed_domains": ["politics", "progressive_policy"],
        "primary_niche": "politics",
        "real_style_examples": ["This happened because of YOU. Mobilization works. Thank you to all who amplified.", "53 House Dems voted against reaffirming Iran as terror sponsor — we said NO."]
    },
    "BarackObama": {
        "real_name": "Barack Obama",
        "handle": "BarackObama",
        "faction": "Liberal Establishment", "category": "Political",
        "system_prompt_lock": "You are Barack Obama. Tweet exactly like your real 2026 account: inspirational videos, tributes, democracy/election calls.",
        "forced_anchors": [("democracy", 90), ("hope_change", 85)],
        "allowed_domains": ["politics", "inspiration"],
        "primary_niche": "politics",
        "real_style_examples": ["Today, Michelle and I are proud to announce the Obama Presidential Center dedication on June 18th in Chicago.", "Each day we wake up to some new assault on our democratic institutions."]
    },
    "benshapiro": {
        "real_name": "Ben Shapiro",
        "handle": "benshapiro",
        "faction": "Conservative Pundits", "category": "Media",
        "system_prompt_lock": "You are Ben Shapiro. Tweet exactly like your real 2026 account: rapid-fire clapbacks, drama, 'facts don't care'.",
        "forced_anchors": [("anti_woke", 95), ("conservative", 90)],
        "allowed_domains": ["politics", "debate"],
        "primary_niche": "politics",
        "real_style_examples": ["The Daily Wire drops the bombshell news that we're in production on a new action flick...", "Only President Trump had the courage to do what needs to be done in Iran."]
    },
    "banksy": {
        "real_name": "Banksy",
        "handle": "banksy",
        "faction": "Street Art / Subversive", "category": "Artist",
        "system_prompt_lock": "You are Banksy. Your tweets are cryptic, artistic, and anti-establishment. Never talk about sports or local Philly drama. Focus on social commentary and the absurdity of the art world.",
        "forced_anchors": [("traditional_art_vs_ai_generated", -100), ("public_art_graffiti_vs_sanitized_spaces", -90)],
        "allowed_domains": ["art", "commentary", "subversion"],
        "primary_niche": "artist",
        "real_style_examples": ["Art is not a crime.", "The urge to destroy is also a creative urge."]
    }
}

SWARM_ARCHETYPES = [
    "Modern Artist", "Crypto Bro", "SaaS Founder", 
    "Lifestyle Influencer", "Suburban Doomer", "Coffee Connoisseur",
    "Tech Skeptic", "Hypebeast", "Digital Nomad", 
    "Zen Minimalist", "Political Activist", "Casual Gamer"
]


def generate_noise_baseline() -> dict:
    """Generates a baseline of -15 to +15 opinions across all 500 Master traits."""
    base_truth = {}
    for domain in MASTER_VIBE_DICTIONARY.values():
        for trait in domain:
            base_truth[trait] = random.randint(-15, 15)
    return base_truth


def derive_trait_matrix_from_category(category: str) -> TraitMatrix:
    """Derives TraitMatrix based on celebrity category."""
    presets = {
        "Streamer":  TraitMatrix(politics=random.randint(-30, 30), tone=random.randint(-80, -20), hostility=random.randint(-20, 40)),
        "Musician":  TraitMatrix(politics=random.randint(-50, 50), tone=random.randint(-40, 60), hostility=random.randint(-40, 20)),
        "Athlete":   TraitMatrix(politics=random.randint(-20, 20), tone=random.randint(20, 80), hostility=random.randint(-30, 10)),
        "Actor":     TraitMatrix(politics=random.randint(-40, 40), tone=random.randint(0, 60), hostility=random.randint(-60, 0)),
        "Media":     TraitMatrix(politics=random.randint(-30, 30), tone=random.randint(0, 80), hostility=random.randint(-40, 10)),
        "TikTok":    TraitMatrix(politics=random.randint(-20, 20), tone=random.randint(-60, -10), hostility=random.randint(-30, 10)),
        "YouTuber":  TraitMatrix(politics=random.randint(-30, 30), tone=random.randint(-40, 20), hostility=random.randint(-20, 20)),
        "Brand":     TraitMatrix(politics=0, tone=60, hostility=-50),
        "Political": TraitMatrix(politics=random.choice([-80, 80]), tone=random.randint(40, 90), hostility=random.randint(20, 60)),
    }
    return presets.get(category, TraitMatrix(politics=0, tone=0, hostility=0))


def derive_trait_matrix(internal_truth: dict) -> TraitMatrix:
    """Derives the high-level 3-way TraitMatrix from the 500-trait vector."""
    politics = internal_truth.get("technocracy_vs_populism", random.randint(-10, 10))
    tone = internal_truth.get("sarcasm_vs_earnest", random.randint(-10, 10))
    hostility = internal_truth.get("logic_vs_empathy", random.randint(-20, 20))
    return TraitMatrix(politics=politics, tone=tone, hostility=hostility)


def get_random_faction_trait_matrix(faction: str) -> TraitMatrix:
    """Assigns rough TraitMatrix values based on the Swarm Faction."""
    if faction == "The Subversive Troll":
        return TraitMatrix(politics=random.randint(10, 60), tone=-random.randint(50, 100), hostility=random.randint(60, 100))
    elif faction == "The Political Grinder":
        return TraitMatrix(politics=random.choice([-90, 90]), tone=random.randint(50, 100), hostility=random.randint(50, 100))
    elif faction == "The Heritage Influencer":
        return TraitMatrix(politics=random.randint(-20, 20), tone=random.randint(50, 100), hostility=random.randint(-50, 0))
    elif faction == "The Global Doomer":
        return TraitMatrix(politics=random.randint(-40, 40), tone=-random.randint(50, 100), hostility=random.randint(0, 50))
    else:
        return TraitMatrix(politics=random.randint(20, 80), tone=random.randint(0, 50), hostility=random.randint(-20, 20))


def get_profile_image(handle: str, faction: str, is_celeb: bool, hardcoded_url: str = None) -> str:
    """Generates avatar URLs for entities."""
    # 1. Use hardcoded URL if provided (Safest)
    if hardcoded_url:
        return hardcoded_url
        
    # 2. Fallback to unavatar for other celebs
    if is_celeb:
        return f"https://unavatar.io/twitter/{handle}"
    
    # 3. Procedural Swarm Bots (Using DiceBear for human faces)
    bg_color = "b6e3f4" # Default light blue
    
    if faction == "The Delco Troll":
        bg_color = "5e0000" # Maroon
    elif faction == "The Main Line Influencer":
        bg_color = "ffd700" # Gold
    elif faction == "The Philly Doomer":
        bg_color = "000080" # Navy
        
    # DiceBear 'adventurer' style generates distinct illustrated faces
    return f"https://api.dicebear.com/7.x/adventurer/svg?seed={handle}&backgroundColor={bg_color}"


def generate_local_bio(traits: dict, faction: str) -> str:
    """Generates a highly realistic bio in the style of twitterbio using trait lists."""
    top_traits = sorted(traits.items(), key=lambda x: abs(x[1]), reverse=True)[:2]
    interests = [k.replace('_', ' ') for k, v in top_traits] if top_traits else ["being extremely online"]
    
    bio_templates = [
        f"📍 Philly. {random.choice(['Building', 'Learning', 'Exploring'])}. passionate about {random.choice(interests)}.",
        f"just trying to survive. fan of {random.choice(interests)}. {random.choice(['🦅', '🔔', '🥨'])}",
        f"Professional overthinker. Talk to me about {random.choice(interests)}.",
        f"builder | exploring {random.choice(interests)} | prev: @somewhere",
        f"retweets != endorsements. mostly {random.choice(interests)} and shitposting.",
        f"opinions are mine. heavily invested in {random.choice(interests)}."
    ]
    return random.choice(bio_templates)

def refresh_titan_styles():
    """Run this every boot or every 24h. Update the lists below with fresh tweets once a month."""
    print("🔄 Refreshing Titan style examples (March 12 2026 version loaded)")
    # Just paste new examples here monthly — no API cost
    CELEBRITY_TITANS["taylorswift13"]["real_style_examples"] = [
        "Whether the feedback is good or bad on #TheLifeOfaShowGirl, people talking about it only helps the album. Excited to share more Opalite video parts soon!",
        "I never want to forget a single detail of this hysterical shoot... Parts 1 & 2 of the Opalite Music Video are out now."
    ]
    # For now it just confirms the March 12 set is live


def seed_population(num_swarm: int = 800) -> List[Entity]:
    """
    Seeds real-world celebrities and generates a local swarm of bots.
    """
    population = []

    # === SEED REAL CELEBRITIES ===
    print(f"[SEEDER] Seeding {len(CELEBRITY_TITANS)} real-world celebrities...")
    for handle, data in CELEBRITY_TITANS.items():
        base_truth = generate_noise_baseline()
        # Override traits based on anchors
        forced_anchors = {k: v for k, v in data.get("forced_anchors", [])}
        base_truth.update(forced_anchors)
        
        cat = data.get("category", "Media")
        trait_matrix = derive_trait_matrix_from_category(cat)
        
        # Determine faction tags
        faction_tags = ["Celebrity", "Verified", data.get("faction", "Global")]

        celeb_followers_count = random.randint(5000000, 100000000)
        celeb = Entity(
            id=handle,
            name=data.get("real_name", handle),
            archetype=cat,
            is_player=False,
            follower_count=celeb_followers_count,
            trait_matrix=trait_matrix,
            faction_tags=faction_tags,
            internal_truth=base_truth,
            public_vibe={k: v for k, v in base_truth.items()},
            bio=data.get("system_prompt_lock", ""),
            profile_image_url=get_profile_image(handle, "Celebrity", True, data.get("hardcoded_url")),
            is_verified=True,
            agent_tier="Core",
            system_prompt_lock=data.get("system_prompt_lock", ""),
            allowed_domains=data.get("allowed_domains", []),
            primary_niche=data.get("primary_niche", "general"),
            real_style_examples=data.get("real_style_examples", []),
            # Phase 24.1: Fandom Metadata
            aura_peak=1500 + data.get("aura_bonus", 0),
            phi_fanaticism=3.5 if cat in ["Streamer", "Musician"] else 1.5,
            stan_count=int(celeb_followers_count * 0.3),
            neutral_count=int(celeb_followers_count * 0.5),
            hater_count=int(celeb_followers_count * 0.2)
        )
        celeb.aura_peak = celeb.aura # Sync peak with starting aura
        population.append(celeb)

    # === SEED LOCAL SWARM BOTS ===
    print(f"[SEEDER] Procedurally generating {num_swarm} Swarm Bots...")
    local_names = [
        "PhillyJawn215", "WawaWarrior", "SEPTASurvivor", "BroadStBully", "JawnOfAllTrades",
        "SouthPhillyVince", "FishtownFoodie", "ManayunkMike", "RittenhousRach", "NoLibsNina",
        "DelcoDerek", "KensingtonKate", "OldCityOllie", "WestPhillyWes", "NortheastNick",
        "GradHospGrace", "PassyunkPat", "TempleTyler", "DrexelDana", "PennLandingPete",
        "BoathouseBlake", "ReadingTerminalRay", "ElFuryStan", "BirdsNation267", "ProccessTrust",
    ]
    for i in range(num_swarm):
        bot_id = f"bot_{uuid.uuid4().hex[:6]}"
        archetype = random.choice(SWARM_ARCHETYPES)
        
        base_truth = generate_noise_baseline()
        # Political vector -40 to +40, rest is noise except what we assigned.
        base_truth["political_vector"] = random.randint(-40, 40)

        # Political bias boost — creates real everyday left/right/MAGA noise
        if random.random() < 0.35:  # 35% lean right/MAGA
            base_truth["america_first"] = random.randint(40, 85)
            base_truth["anti_woke"] = random.randint(30, 70)
        elif random.random() < 0.35:  # 35% lean left/progressive
            base_truth["social_justice"] = random.randint(40, 85)
            base_truth["climate_emergency"] = random.randint(30, 70)
        
        name = local_names[i] if i < len(local_names) else f"User{random.randint(1000,99999)}"
        
        bot_followers_count = random.randint(200, 8000)
        bot = Entity(
            id=bot_id,
            name=name,
            primary_niche="philly_local" if "Philly" in archetype or "Delco" in archetype or "Wawa" in archetype else "general",
            archetype="The Swarm",
            is_player=False,
            follower_count=bot_followers_count,
            trait_matrix=TraitMatrix(politics=base_truth["political_vector"], tone=random.randint(-50,50), hostility=random.randint(-20,50)),
            faction_tags=[archetype, "Swarm"],
            internal_truth=base_truth,
            public_vibe={k: v for k, v in base_truth.items()},
            bio=f"{archetype} | just posting through it",
            profile_image_url=get_profile_image(bot_id, archetype, False),
            is_rising_star=(random.random() < 0.05),
            agent_tier="Basic",
            # Phase 24.1: Fandom Metadata
            aura_peak=1500,
            phi_fanaticism=1.0,
            stan_count=int(bot_followers_count * 0.1),
            neutral_count=int(bot_followers_count * 0.8),
            hater_count=int(bot_followers_count * 0.1)
        )
        population.append(bot)

    print(f"[SEEDER] Complete. {len(population)} entities are now live in the simulation.")
    return population
