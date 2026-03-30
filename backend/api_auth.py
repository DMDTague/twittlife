"""
Authentication and Character Creation API Endpoints
Phase 28: Player Journey
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
import logging
from datetime import datetime
from database_supabase import db
from supabase import Client as SupabaseClient
import os
from supabase import create_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=50)

class SignUpResponse(BaseModel):
    user_id: str
    email: str
    username: str
    message: str = "User created successfully"

class HandleCheckRequest(BaseModel):
    handle: str = Field(..., min_length=3, max_length=25)

class HandleCheckResponse(BaseModel):
    handle: str
    available: bool

class NicheOption(BaseModel):
    id: str
    name: str
    description: str
    bonus_stat: str
    bonus_value: int

class CreateCharacterRequest(BaseModel):
    handle: str = Field(..., min_length=3, max_length=25)
    niche: str = Field(..., min_length=3)  # tech, politics, combat_sports, gaming, general
    stats: dict = Field(..., description="Rolled stats: {aura, heat, insight}")

class CreateCharacterResponse(BaseModel):
    game_state_id: int
    player_id: str
    handle: str
    niche: str
    starting_aura: int
    starting_followers: int
    starting_wealth: int
    generation: int = 1
    message: str = "Character created successfully"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_supabase_client():
    """Get Supabase client for API operations"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    return create_client(url, key)

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract user from JWT token in Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = authorization.split(" ")[1]
    supabase = get_supabase_client()
    
    try:
        user = supabase.auth.get_user(token)
        if user and user.user:
            return user.user
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# HANDLE VALIDATION
# ============================================================================

@router.post("/check-handle", response_model=HandleCheckResponse)
async def check_handle_availability(request: HandleCheckRequest):
    """
    Check if a handle/username is available
    """
    # Validate format
    if not request.handle.replace("_", "").isalnum():
        return HandleCheckResponse(
            handle=request.handle,
            available=False
        )
    
    # Check in database
    available = await db.check_username_available(request.handle)
    
    return HandleCheckResponse(
        handle=request.handle,
        available=available
    )

# ============================================================================
# NICHE DATA
# ============================================================================

NICHE_DATA = {
    "tech": NicheOption(
        id="tech",
        name="Tech",
        description="Contrarian, intellectual, startup-focused",
        bonus_stat="insight",
        bonus_value=20
    ),
    "politics": NicheOption(
        id="politics",
        name="Politics",
        description="Ideological, polarized, current-events",
        bonus_stat="heat",
        bonus_value=20
    ),
    "combat_sports": NicheOption(
        id="combat_sports",
        name="Combat Sports",
        description="Aggressive, tribalistic, fitness-focused",
        bonus_stat="heat",
        bonus_value=20
    ),
    "gaming": NicheOption(
        id="gaming",
        name="Gaming",
        description="Casual, community-focused, entertainment",
        bonus_stat="aura",
        bonus_value=20
    ),
    "general": NicheOption(
        id="general",
        name="General",
        description="Balanced, no niche bonus",
        bonus_stat="none",
        bonus_value=0
    )
}

@router.get("/niches")
async def get_niche_data():
    """
    Get all available niches with bonuses
    """
    return {
        "niches": list(NICHE_DATA.values())
    }

# ============================================================================
# CHARACTER CREATION
# ============================================================================

@router.post("/create-character", response_model=CreateCharacterResponse)
async def create_character(
    request: CreateCharacterRequest,
    current_user = Depends(get_current_user)
):
    """
    Create a new character for the current user
    Process:
    1. Validate handle availability
    2. Get or create account record
    3. Create Entity (player character)
    4. Create game state with starting stats
    5. Apply niche bonuses
    """
    
    user_id = current_user.id
    
    # ========== STEP 1: Validate Handle ==========
    handle_available = await db.check_username_available(request.handle)
    if not handle_available:
        raise HTTPException(status_code=400, detail=f"Handle '{request.handle}' is already taken")
    
    # ========== STEP 2: Validate Niche ==========
    if request.niche not in NICHE_DATA:
        raise HTTPException(status_code=400, detail=f"Invalid niche: {request.niche}")
    
    niche_info = NICHE_DATA[request.niche]
    
    # ========== STEP 3: Apply Niche Bonuses to Stats ==========
    starting_stats = request.stats.copy()
    
    # Apply niche bonus
    if niche_info.bonus_stat != "none":
        bonus_key = niche_info.bonus_stat.lower()
        if bonus_key in starting_stats:
            starting_stats[bonus_key] += niche_info.bonus_value
    
    # Ensure stats are within bounds (0-100)
    for key in starting_stats:
        starting_stats[key] = max(0, min(100, starting_stats[key]))
    
    # ========== STEP 4: Get or Create Account ==========
    account = await db.get_account(user_id)
    if not account:
        # Create new account
        account = await db.create_account(user_id, request.handle)
        generation = 1
    else:
        # Existing account starting new generation
        generation = account.get('total_generations', 1) + 1
        await db.update_account(user_id, {
            'current_generation': generation,
            'total_generations': generation
        })
    
    # ========== STEP 5: Create Player Entity ==========
    player_id = f"player_{user_id}"
    
    # Build trait matrix based on niche and stats
    trait_matrix = {
        "politics": 0,      # Neutral to start
        "tone": starting_stats.get("insight", 50) - 50,  # Insight → tone
        "hostility": starting_stats.get("heat", 50) - 50   # Heat → hostility
    }
    
    entity_data = {
        "id": player_id,
        "user_id": user_id,
        "name": request.handle,
        "primary_niche": request.niche,
        "bio": f"Gen {generation} {request.niche.replace('_', ' ').title()}",
        "is_player": True,
        "follower_count": 500,
        "account_tier": "guest",
        "trait_matrix": trait_matrix,
        "aura": 1500,
        "wealth": 0,
        "heat": starting_stats.get("heat", 50),
        "status": "Active"
    }
    
    try:
        entity_result = await db.create_entity(entity_data)
        entity_id = entity_result.get('id', player_id)
    except Exception as e:
        logger.error(f"Failed to create player entity: {e}")
        raise HTTPException(status_code=500, detail="Failed to create character")
    
    # ========== STEP 6: Create Game State ==========
    initial_game_stats = {
        "aura": 1500 + starting_stats.get("aura", 0),
        "followers": 500,
        "wealth": 0
    }
    
    try:
        game_state = await db.create_game_state(
            user_id=user_id,
            generation=generation,
            player_entity_id=entity_id,
            initial_stats=initial_game_stats
        )
        game_state_id = game_state.get('id', 0)
    except Exception as e:
        logger.error(f"Failed to create game state: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize game")
    
    # ========== RETURN RESPONSE ==========
    return CreateCharacterResponse(
        game_state_id=game_state_id,
        player_id=entity_id,
        handle=request.handle,
        niche=request.niche,
        starting_aura=initial_game_stats['aura'],
        starting_followers=initial_game_stats['followers'],
        starting_wealth=initial_game_stats['wealth'],
        generation=generation
    )

@router.get("/current-character")
async def get_current_character(current_user = Depends(get_current_user)):
    """
    Get current character data for authenticated user
    """
    user_id = current_user.id
    
    # Get latest account
    account = await db.get_account(user_id)
    if not account:
        raise HTTPException(status_code=404, detail="No account found")
    
    # Get active game state
    game_state = await db.get_active_game_state(user_id)
    if not game_state:
        # User hasn't created character yet
        raise HTTPException(status_code=404, detail="Create a character first")
    
    # Get player entity
    entity = await db.get_player_entity(user_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "account": account,
        "game_state": game_state,
        "entity": entity
    }
