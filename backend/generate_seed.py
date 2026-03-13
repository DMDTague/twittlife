import json
import os

seed_data = [
    {
        "handle": "elonmusk",
        "name": "Elon Musk",
        "bio": "Occasional poster. Mars enthusiast.",
        "followers": 150000000,
        "faction_tags": ["The Tech Visionaries", "Celebrity"],
        "is_verified": True,
        "internal_truth": {},
        "public_vibe": {}
    },
    {
        "handle": "MayorCherelle",
        "name": "Cherelle Parker",
        "bio": "100th Mayor of Philadelphia. One Philly, a united city.",
        "followers": 55000,
        "faction_tags": ["The Incumbents", "Celebrity"],
        "is_verified": True,
        "internal_truth": {},
        "public_vibe": {}
    },
    {
        "handle": "GrittyNHL",
        "name": "Gritty",
        "bio": "It me.",
        "followers": 850000,
        "faction_tags": ["The Delco Trolls", "Celebrity"],
        "is_verified": True,
        "internal_truth": {},
        "public_vibe": {}
    },
    {
        "handle": "SEPTA_SOCIAL",
        "name": "SEPTA",
        "bio": "Official SEPTA Customer Service. We're trying our best.",
        "followers": 120000,
        "faction_tags": ["The Centrists"],
        "is_verified": True,
        "internal_truth": {},
        "public_vibe": {}
    },
    {
        "handle": "taylorswift13",
        "name": "Taylor Swift",
        "bio": "I'm the problem, it's me.",
        "followers": 95000000,
        "faction_tags": ["The Main Line Influencer", "Celebrity"],
        "is_verified": True,
        "internal_truth": {},
        "public_vibe": {}
    }
]

# Save to the backend directory
file_path = os.path.join(os.path.dirname(__file__), "celebrity_seed_full.json")
with open(file_path, "w") as f:
    json.dump(seed_data, f, indent=4)

print(f"Successfully generated {len(seed_data)} Titans with corrected handle keys in {file_path}!")
