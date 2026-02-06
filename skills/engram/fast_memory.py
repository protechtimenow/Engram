"""
Fast Memory Module - Mind Modality for Engram
Quick context recall and caching for fast responses
"""

import time
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class MindModality:
    """
    Fast memory system for Engram agent
    - Caches recent conversations
    - Quick context recall
    - TTL-based expiration
    """
    
    def __init__(self, ttl_seconds: int = 300, max_context: int = 10):
        self.cache: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}
        self.ttl = ttl_seconds
        self.max_context = max_context
        self.context_window: List[Dict[str, Any]] = []
        
        # Memory file for persistence
        self.memory_file = "memory/engram_mind.json"
        self._load_memory()
    
    def _load_memory(self):
        """Load persistent memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.cache = data.get('cache', {})
                    self.timestamps = data.get('timestamps', {})
                    self.context_window = data.get('context', [])[-self.max_context:]
            except Exception:
                pass
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump({
                    'cache': self.cache,
                    'timestamps': self.timestamps,
                    'context': self.context_window[-self.max_context:],
                    'last_updated': datetime.now().isoformat()
                }, f)
        except Exception:
            pass
    
    def recall(self, key: str) -> Optional[Any]:
        """Quick recall from memory"""
        now = time.time()
        
        if key in self.cache:
            timestamp = self.timestamps.get(key, 0)
            if now - timestamp < self.ttl:
                return self.cache[key]
            else:
                # Expired
                del self.cache[key]
                del self.timestamps[key]
        
        return None
    
    def remember(self, key: str, value: Any, persist: bool = False):
        """Store in memory"""
        self.cache[key] = value
        self.timestamps[key] = time.time()
        
        if persist:
            self._save_memory()
    
    def add_context(self, role: str, content: str):
        """Add to context window"""
        self.context_window.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Trim to max size
        if len(self.context_window) > self.max_context:
            self.context_window = self.context_window[-self.max_context:]
    
    def get_context(self) -> List[Dict[str, str]]:
        """Get recent context for prompts"""
        return [
            {'role': item['role'], 'content': item['content']}
            for item in self.context_window[-self.max_context:]
        ]
    
    def quick_recall(self, query: str) -> Optional[str]:
        """
        Fast pattern matching for common queries
        Returns cached response if available
        """
        # Normalize query
        query_lower = query.lower().strip()
        
        # Check cache
        cached = self.recall(f"query:{query_lower}")
        if cached:
            return cached
        
        # Pattern matching for quick responses
        quick_patterns = {
            'status': lambda: self._get_status(),
            'help': lambda: self._get_help(),
            'ping': lambda: '🏓 Pong! Fast mode active.',
            'hello': lambda: '👋 Hello! Engram Fast Mode ready.',
            'hi': lambda: '👋 Hi there! Ready to assist.',
        }
        
        for pattern, handler in quick_patterns.items():
            if pattern in query_lower:
                response = handler()
                self.remember(f"query:{query_lower}", response)
                return response
        
        return None
    
    def _get_status(self) -> str:
        """Quick status check"""
        return f"""[Engram Fast Mode Status]
✅ Mind Modality: Active
💾 Cache Size: {len(self.cache)} items
💬 Context Window: {len(self.context_window)} messages
⏱️ TTL: {self.ttl}s
🚀 Mode: FAST (15s timeout)"""
    
    def _get_help(self) -> str:
        """Quick help"""
        return """[Engram Fast Commands]
/status - Quick status check
/analyze <pair> - Fast market analysis
/signal <pair> - Trading signal
/help - This message

Fast mode: 15s timeout, streaming ON"""
    
    def clear(self):
        """Clear all memory"""
        self.cache.clear()
        self.timestamps.clear()
        self.context_window.clear()
        self._save_memory()


# Global instance
_mind_instance: Optional[MindModality] = None

def get_mind(ttl_seconds: int = 300, max_context: int = 10) -> MindModality:
    """Get or create global mind instance"""
    global _mind_instance
    if _mind_instance is None:
        _mind_instance = MindModality(ttl_seconds, max_context)
    return _mind_instance
