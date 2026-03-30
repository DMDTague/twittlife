"""
Supabase Database Client
Handles all connections to PostgreSQL via Supabase
"""

import os
import logging
from typing import Optional, List, Dict, Any
from supabase import create_client, Client as SupabaseClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Database:
    """Singleton database connection manager"""
    _instance: Optional['Database'] = None
    _client: Optional[SupabaseClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Supabase client"""
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        self._client = create_client(url, key)
        logger.info(f"✓ Connected to Supabase: {url}")
    
    @property
    def client(self) -> SupabaseClient:
        """Get Supabase client"""
        if self._client is None:
            self._initialize()
        return self._client
    
    # ============================================================================
    # ACCOUNTS (User metadata)
    # ============================================================================
    
    async def create_account(self, user_id: str, username: str) -> Dict[str, Any]:
        """Create new user account record"""
        try:
            response = self.client.table('accounts').insert({
                'id': user_id,
                'username': username,
                'current_generation': 1,
                'total_generations': 1
            }).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to create account: {e}")
            raise
    
    async def get_account(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user account by ID"""
        try:
            response = self.client.table('accounts').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get account: {e}")
            return None
    
    async def get_account_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user account by username"""
        try:
            response = self.client.table('accounts').select('*').eq('username', username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get account by username: {e}")
            return None
    
    async def check_username_available(self, username: str) -> bool:
        """Check if username is available"""
        try:
            response = self.client.table('accounts').select('id').eq('username', username).execute()
            return len(response.data) == 0
        except Exception as e:
            logger.error(f"Failed to check username: {e}")
            return False
    
    async def update_account(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user account"""
        try:
            response = self.client.table('accounts').update(data).eq('id', user_id).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to update account: {e}")
            raise
    
    # ============================================================================
    # GAME STATES (Current game session)
    # ============================================================================
    
    async def create_game_state(
        self, 
        user_id: str, 
        generation: int, 
        player_entity_id: str,
        initial_stats: Dict[str, int]
    ) -> Dict[str, Any]:
        """Create new game state for generation"""
        try:
            response = self.client.table('game_states').insert({
                'user_id': user_id,
                'generation_number': generation,
                'player_entity_id': player_entity_id,
                'current_aura': initial_stats.get('aura', 1500),
                'current_followers': initial_stats.get('followers', 500),
                'current_wealth': initial_stats.get('wealth', 0),
                'current_tier': 'guest',
                'status': 'active'
            }).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to create game state: {e}")
            raise
    
    async def get_game_state(self, user_id: str, generation: int) -> Optional[Dict[str, Any]]:
        """Get current game state"""
        try:
            response = self.client.table('game_states').select('*').eq('user_id', user_id).eq('generation_number', generation).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get game state: {e}")
            return None
    
    async def get_active_game_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get latest active game state for user"""
        try:
            response = self.client.table('game_states').select('*').eq('user_id', user_id).eq('status', 'active').order('generation_number', desc=True).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get active game state: {e}")
            return None
    
    async def update_game_state(self, user_id: str, generation: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update game state"""
        try:
            response = self.client.table('game_states').update(data).eq('user_id', user_id).eq('generation_number', generation).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to update game state: {e}")
            raise
    
    # ============================================================================
    # ACCOUNT GENERATIONS (History tracking)
    # ============================================================================
    
    async def save_generation(
        self,
        user_id: str,
        generation: int,
        handle: str,
        niche: str,
        starting_stats: Dict[str, int],
        ending_stats: Dict[str, int],
        deplatform_reason: Optional[str] = None,
        legacy_bonuses: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """Save completed generation to history"""
        if legacy_bonuses is None:
            legacy_bonuses = {}
        
        try:
            response = self.client.table('account_generations').insert({
                'user_id': user_id,
                'generation_number': generation,
                'handle': handle,
                'niche': niche,
                'starting_stats': starting_stats,
                'ending_stats': ending_stats,
                'deplatform_reason': deplatform_reason,
                'legacy_aura_bonus': legacy_bonuses.get('aura', 0),
                'legacy_wealth_bonus': legacy_bonuses.get('wealth', 0),
                'legacy_follower_bonus': legacy_bonuses.get('followers', 0)
            }).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to save generation: {e}")
            raise
    
    async def get_account_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all generations for user"""
        try:
            response = self.client.table('account_generations').select('*').eq('user_id', user_id).order('generation_number').execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to get account history: {e}")
            return []
    
    # ============================================================================
    # ENTITIES (NPCs + Player character data)
    # ============================================================================
    
    async def create_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new NPC or player entity"""
        try:
            response = self.client.table('entities').insert(entity_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to create entity: {e}")
            raise
    
    async def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID"""
        try:
            response = self.client.table('entities').select('*').eq('id', entity_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get entity: {e}")
            return None
    
    async def get_player_entity(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get player entity for user"""
        try:
            response = self.client.table('entities').select('*').eq('user_id', user_id).eq('is_player', True).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get player entity: {e}")
            return None
    
    async def get_all_npcs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all NPCs (non-player entities)"""
        try:
            response = self.client.table('entities').select('*').eq('is_player', False).limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to get NPCs: {e}")
            return []
    
    async def update_entity(self, entity_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update entity"""
        try:
            response = self.client.table('entities').update(data).eq('id', entity_id).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to update entity: {e}")
            raise
    
    async def get_entities_by_niche(self, niche: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get entities by niche"""
        try:
            response = self.client.table('entities').select('*').eq('primary_niche', niche).limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to get entities by niche: {e}")
            return []
    
    # ============================================================================
    # EVENTS (Tweets, replies, etc.)
    # ============================================================================
    
    async def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new event (tweet, reply, etc.)"""
        try:
            response = self.client.table('events').insert(event_data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise
    
    async def get_feed(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get global feed"""
        try:
            response = self.client.table('events').select('*').order('timestamp', desc=True).range(offset, offset + limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to get feed: {e}")
            return []
    
    async def get_entity_events(self, entity_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events for specific entity"""
        try:
            response = self.client.table('events').select('*').eq('entity_id', entity_id).order('timestamp', desc=True).limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to get entity events: {e}")
            return []

# Singleton instance
db = Database()
