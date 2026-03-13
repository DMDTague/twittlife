"""
Phase 19: Rate Limiter & Caching Layer for TwitLife
Provides token budget tracking, request throttling, and an in-memory TTL cache
to prevent the simulation from burning through Groq API limits during Faction Wars.
"""
import time
import threading
from collections import defaultdict
from functools import wraps


class GroqRateLimiter:
    """
    Token-aware rate limiter for Groq API calls.
    Tracks requests per minute (RPM) and tokens per minute (TPM).
    Thread-safe via locks.
    """
    def __init__(self, max_rpm: int = 30, max_tpm: int = 6000, budget_tokens_per_day: int = 500_000):
        self.max_rpm = max_rpm
        self.max_tpm = max_tpm
        self.budget_tokens_per_day = budget_tokens_per_day
        
        self._lock = threading.Lock()
        self._request_timestamps: list[float] = []
        self._token_log: list[tuple[float, int]] = []  # (timestamp, tokens_used)
        self._daily_tokens_used = 0
        self._daily_reset_time = time.time()
        
        # Stats
        self.total_requests = 0
        self.total_tokens = 0
        self.throttled_count = 0

    def _prune_old_entries(self, now: float):
        """Remove entries older than 60 seconds."""
        cutoff = now - 60.0
        self._request_timestamps = [t for t in self._request_timestamps if t > cutoff]
        self._token_log = [(t, tok) for t, tok in self._token_log if t > cutoff]

    def can_proceed(self, estimated_tokens: int = 300) -> tuple[bool, str]:
        """
        Check if a request can proceed without violating limits.
        Returns (allowed: bool, reason: str).
        """
        now = time.time()
        with self._lock:
            self._prune_old_entries(now)
            
            # Daily budget check
            if now - self._daily_reset_time > 86400:
                self._daily_tokens_used = 0
                self._daily_reset_time = now
            
            if self._daily_tokens_used + estimated_tokens > self.budget_tokens_per_day:
                self.throttled_count += 1
                return False, f"Daily token budget exhausted ({self._daily_tokens_used}/{self.budget_tokens_per_day})"
            
            # RPM check
            if len(self._request_timestamps) >= self.max_rpm:
                self.throttled_count += 1
                wait_time = 60 - (now - self._request_timestamps[0])
                return False, f"RPM limit ({self.max_rpm}/min). Retry in {wait_time:.1f}s"
            
            # TPM check
            current_tpm = sum(tok for _, tok in self._token_log)
            if current_tpm + estimated_tokens > self.max_tpm:
                self.throttled_count += 1
                return False, f"TPM limit ({current_tpm}/{self.max_tpm})"
            
            return True, "OK"

    def record_usage(self, tokens_used: int):
        """Record a completed API call."""
        now = time.time()
        with self._lock:
            self._request_timestamps.append(now)
            self._token_log.append((now, tokens_used))
            self._daily_tokens_used += tokens_used
            self.total_requests += 1
            self.total_tokens += tokens_used

    def get_stats(self) -> dict:
        """Return current usage statistics."""
        now = time.time()
        with self._lock:
            self._prune_old_entries(now)
            return {
                "rpm_current": len(self._request_timestamps),
                "rpm_limit": self.max_rpm,
                "tpm_current": sum(tok for _, tok in self._token_log),
                "tpm_limit": self.max_tpm,
                "daily_tokens_used": self._daily_tokens_used,
                "daily_budget": self.budget_tokens_per_day,
                "total_requests": self.total_requests,
                "total_tokens": self.total_tokens,
                "throttled_count": self.throttled_count
            }


class VibeCache:
    """
    In-memory TTL cache for expensive computations like Trending Topics
    and Global Heatmaps. Avoids re-scanning the entire event list on every heartbeat.
    """
    def __init__(self, default_ttl: int = 30):
        self.default_ttl = default_ttl  # seconds
        self._cache: dict[str, tuple[float, any]] = {}  # key -> (expires_at, value)
        self._lock = threading.Lock()

    def get(self, key: str):
        """Retrieve cached value. Returns None if expired or missing."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.time() > expires_at:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value, ttl: int = None):
        """Store a value with optional custom TTL."""
        with self._lock:
            self._cache[key] = (time.time() + (ttl or self.default_ttl), value)

    def invalidate(self, key: str):
        """Force-expire a cached entry."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self):
        """Flush all cached entries."""
        with self._lock:
            self._cache.clear()


# Singleton instances for the application
rate_limiter = GroqRateLimiter(max_rpm=30, max_tpm=6000, budget_tokens_per_day=500_000)
vibe_cache = VibeCache(default_ttl=30)  # 30-second TTL for trending topics
