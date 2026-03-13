"""
TwitLife Master Vibe Dictionary
This file contains the extensive lists of dichotomies used by the GameEngine to tag Tweets and generate NPC Friction.
Each value exists on a scale from -100 to +100.
"""

MASTER_VIBE_DICTIONARY = {
    "political_and_civic": [
        "protectionism_vs_free_trade", 
        "wealth_tax_vs_flat_tax", 
        "ubi_vs_work_for_benefits", 
        "central_bank_vs_defi",
        "technocracy_vs_populism", 
        "federal_power_vs_states_rights", 
        "mandatory_voting_vs_voluntary_abstention", 
        "term_limits_vs_incumbency",
        "restorative_justice_vs_retributive", 
        "privacy_vs_public_safety", 
        "gun_control_vs_self_defense", 
        "border_security_vs_open_borders",
        "meritocracy_vs_equity", 
        "traditional_family_vs_chosen_family", 
        "religious_law_vs_secularism", 
        "patriotism_vs_post_nationalism",
        "isolationism_vs_interventionism", 
        "nato_support_vs_non_alignment", 
        "space_exploration_vs_earth_first"
    ],
    "lifestyle_and_aesthetic": [
        "minimalist_vs_maximalist", 
        "house_plants_vs_low_maintenance", 
        "smart_home_vs_analog", 
        "rural_farmhouse_vs_brutalist_apartment",
        "fast_fashion_vs_thrifting", 
        "comfort_sweats_vs_high_fashion", 
        "socks_with_sandals_ok_vs_fashion_crime", 
        "piercings_vs_no_tattoos",
        "early_riser_vs_night_owl", 
        "morning_coffee_vs_midnight_snack", 
        "routine_vs_spontaneity", 
        "hustle_culture_vs_quiet_quitting",
        "physical_media_vs_streaming", 
        "subtitles_vs_dubbing", 
        "movie_theater_vs_home_setup", 
        "binge_watching_vs_weekly_release",
        "apple_ecosystem_vs_android_freedom", 
        "pc_master_race_vs_console_peasant", 
        "vr_believer_vs_analog_experience", 
        "privacy_first_vs_public_exhibitionist",
        "dark_mode_vs_light_mode_user",
        "cat_person_vs_dog_person",
        "nature_lover_vs_city_slicker"
    ],
    "food_drink_and_petty_culinary": [
        "wawa_vs_sheetz", 
        "mcdonalds_vs_burger_king", 
        "popeyes_vs_chick_fil_a", 
        "wendys_vs_taco_bell",
        "no_toppings_vs_the_works", 
        "pineapple_on_pizza_vs_italian_purist", 
        "bone_in_wings_vs_boneless", 
        "well_done_steak_vs_rare",
        "diet_coke_vs_regular", 
        "sparkling_water_vs_still", 
        "craft_beer_vs_domestic_light", 
        "matcha_vs_espresso",
        "fine_dining_vs_street_food", 
        "tab_splitter_vs_ill_get_it_next_time", 
        "ketchup_on_eggs_vs_disgust",
        "sweet_tooth_vs_savory_lover",
        "vegan_vs_carnivore",
        "home_cook_vs_takeout_king"
    ],
    "art_and_creative_culture": [
        "traditional_art_vs_ai_generated", 
        "gallery_exclusive_vs_digital_open_access", 
        "starving_artist_vs_commercial_success", 
        "abstract_expressionism_vs_hyper_realism",
        "niche_mastery_vs_mass_appeal", 
        "physical_exhibits_vs_virtual_showcases", 
        "independent_creator_vs_studio_signed", 
        "analog_craft_vs_digital_perfection",
        "minimalist_design_vs_complex_ornamentation",
        "public_art_graffiti_vs_sanitized_spaces"
    ],
    "abstract_moral_neurotic": [
        "simulation_theory_vs_hard_reality", 
        "fate_vs_chaos_free_will", 
        "alien_believer_vs_fermi_paradox", 
        "reincarnation_vs_the_void",
        "sarcasm_irony_vs_earnestness", 
        "vague_posting_vs_oversharing", 
        "grammar_nazi_vs_slang_user", 
        "thread_maker_vs_shit_poster",
        "optimist_vs_doomer_nihilist", 
        "empathetic_vs_logic_only", 
        "conflict_seeker_vs_people_pleaser", 
        "extrovert_vs_introvert",
        "monogamy_vs_polyamory", 
        "kids_vs_child_free", 
        "ghosting_vs_closure", 
        "long_distance_vs_proximal",
        "remote_work_vs_office_culture", 
        "four_day_work_week_vs_grindset", 
        "entrepreneur_vs_corporate_stability",
        "forgive_forget_vs_grudge_holder",
        "utilitarian_vs_deontological"
    ]
}

def get_all_dict_keys() -> list[str]:
    """Returns a flat list of all dichotomy strings for LLM injection."""
    keys = []
    for category in MASTER_VIBE_DICTIONARY.values():
        keys.extend(category)
    return keys

# Swarm Ancestry DNA (-100 to 100). The rest of their traits will be -15 to +15 noise.
FACTION_DNA = {
    "The Global Heritage Influencer": {
        "minimalist_vs_maximalist": -80,
        "fast_fashion_vs_thrifting": 90,
        "starving_artist_vs_commercial_success": 80,
        "sarcasm_irony_vs_earnestness": 85,
        "fine_dining_vs_street_food": -90,
        "sweet_tooth_vs_savory_lover": -80
    },
    "The Subversive Troll": {
        "independent_creator_vs_studio_signed": 90,
        "empathetic_vs_logic_only": 85,
        "conflict_seeker_vs_people_pleaser": -95,
        "traditional_art_vs_ai_generated": -100,
        "public_art_graffiti_vs_sanitized_spaces": 85
    },
    "The Tech Visionary": {
        "apple_ecosystem_vs_android_freedom": -95,
        "pc_master_race_vs_console_peasant": -90,
        "optimist_vs_doomer_nihilist": -80,
        "smart_home_vs_analog": -95,
        "simulation_theory_vs_hard_reality": -100
    },
    "The Political Grinder": {
        "technocracy_vs_populism": -90,
        "conflict_seeker_vs_people_pleaser": -85,
        "sarcasm_irony_vs_earnestness": 100,
        "thread_maker_vs_shit_poster": -90
    },
    "The Global Doomer": {
        "optimist_vs_doomer_nihilist": 90,
        "independent_creator_vs_studio_signed": 85,
        "starving_artist_vs_commercial_success": -80
    }
}

FACTION_ANCHORS = {
    "MAGA Titans": [("america_first", 95), ("anti_woke", 90), ("immigration_hard", 85)],
    "Progressive Left": [("social_justice", 95), ("climate_emergency", 90), ("anti_capitalism", 80)],
    "Liberal Hollywood": [("feminism", 85), ("lgbtq", 90), ("celebrity_activism", 70)],
    "Libertarian Tech Bros": [("free_speech_absolutist", 95), ("crypto", 80), ("anti_regulation", 75)],
    "Comedy Central": [("irony_max", 90), ("cancel_culture_skeptic", 70), ("absurd_humor", 95)],
    "Global Doomer": [], 
    "Subversive Troll": [],
    "Heritage Influencer": []
}

# The Fixed Titans of the Simulation
CELEBRITY_REGISTRY = {
    "charlie_mc_villain": {
        "name": "Charlie",
        "archetype": "The Villain",
        "anchors": {"wawa_vs_sheetz": 100, "center_city_vs_the_northeast": 80, "pothole_complainer_vs_pothole_survivor": -90},
        "trait_matrix": {"politics": 0, "tone": -100, "hostility": -60}
    },
    "mayor_cherelle": {
        "name": "Mayor Cherelle",
        "archetype": "The Incumbent",
        "anchors": {"pothole_complainer_vs_pothole_survivor": 90, "septa_defender_vs_septa_hater": -100, "meritocracy_vs_equity": 60},
        "trait_matrix": {"politics": -40, "tone": 80, "hostility": -20}
    },
    "gritty_official": {
        "name": "Gritty",
        "archetype": "Chaos Mascot",
        "anchors": {"gritty_is_god_vs_gritty_is_terrifying": -100, "sarcasm_irony_vs_earnestness": -100, "routine_vs_spontaneity": 100},
        "trait_matrix": {"politics": 0, "tone": -100, "hostility": 50}
    },
    "bryce_harper": {
        "name": "Bryce Harper",
        "archetype": "The Golden Boy",
        "anchors": {"eagles_optimist_vs_doomsday_fan": -90, "hustle_culture_vs_quiet_quitting": -95, "wawa_vs_sheetz": -80},
        "trait_matrix": {"politics": 10, "tone": 60, "hostility": -10}
    }
}

# --- Phase 17: Neighborhood Hubs ---
# Each hub defines the faction tags that "belong" there, anchor traits to vibe-check outsiders,
# and the hostility multiplier applied when an outsider posts in the wrong neighborhood.
NEIGHBORHOOD_HUBS = {
    "The Gallery District": {
        "description": "The artistic & creative epicenter. Pro-originality, anti-corporate.",
        "allowed_tags": ["The_Global_Doomer", "The_Subversive_Troll", "Artist"],
        "vibe_anchors": {
            "individual_creator_vs_studio_signed": (50, 100),
            "traditional_art_vs_ai_generated": (-100, -20),
            "minimalist_design_vs_complex_ornamentation": (-100, -20),
        },
        "outsider_hostility_bonus": 40,
    },
    "The Industrial Hub": {
        "description": "Blue-collar, tech-adjacent manufacturing and legacy industries.",
        "allowed_tags": ["The_Subversive_Troll", "The_Global_Doomer", "Industrial"],
        "vibe_anchors": {
            "pc_master_race_vs_console_peasant": (50, 100),
            "smart_home_vs_analog": (-100, -30),
            "routine_vs_spontaneity": (30, 100),
        },
        "outsider_hostility_bonus": 50,
    },
    "The Financial Plaza": {
        "description": "The elite financial and technological core. High stakes, high polish.",
        "allowed_tags": ["The_Heritage_Influencer", "The_Tech_Visionary", "Financial"],
        "vibe_anchors": {
            "fine_dining_vs_street_food": (-100, -40),
            "fast_fashion_vs_thrifting": (50, 100),
            "comfort_sweats_vs_high_fashion": (40, 100),
        },
        "outsider_hostility_bonus": 30,
    },
}
