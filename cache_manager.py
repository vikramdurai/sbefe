import os
import json
from datetime import datetime, timedelta
from google import genai
from config import GEMINI_API_KEY

class CacheManager:
    """
    Manages Gemini context caching for static design documents.
    Caches are stored server-side and referenced by name to reduce token usage.
    """
    
    def __init__(self, cache_metadata_path="cache_metadata.json"):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.cache_metadata_path = cache_metadata_path
        self.cache_metadata = self._load_metadata()
        
    def _load_metadata(self):
        """Load cache metadata from disk if it exists."""
        if os.path.exists(self.cache_metadata_path):
            try:
                with open(self.cache_metadata_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        with open(self.cache_metadata_path, 'w') as f:
            json.dump(self.cache_metadata, f, indent=2)
    
    def create_design_doc_cache(self, design_docs):
        """
        Creates a cached context from design documents.
        
        Args:
            design_docs: Dict with keys like 'design_doc', 'turn_guide', etc.
                        and values as the document content strings.
        
        Returns:
            Cache name/identifier to use in subsequent API calls.
        """
        # Combine all design docs into structured content
        cache_content = self._format_design_docs(design_docs)
        
        try:
            # Create cached content using Gemini's caching API
            # Note: Caches expire after 1 hour of inactivity by default
            cache = self.client.caches.create(
                model='models/gemini-2.0-flash-001',
                config=genai.types.CreateCachedContentConfig(
                    display_name="sburb_design_docs",
                    system_instruction=cache_content,
                    ttl="3600s"  # 1 hour TTL
                )
            )
            
            # Store metadata
            self.cache_metadata = {
                'cache_name': cache.name,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=1)).isoformat(),
                'doc_keys': list(design_docs.keys())
            }
            self._save_metadata()
            
            print(f"✓ Created cache: {cache.name}")
            return cache.name
            
        except Exception as e:
            print(f"⚠ Cache creation failed: {e}")
            print("  Falling back to non-cached mode")
            return None
    
    def _format_design_docs(self, design_docs):
        """Format design documents for caching."""
        sections = []
        
        if 'design_doc' in design_docs:
            sections.append(f"<DESIGN_DOC>\n{design_docs['design_doc']}\n</DESIGN_DOC>")
        
        if 'turn_guide' in design_docs:
            sections.append(f"<TURN_GUIDE>\n{design_docs['turn_guide']}\n</TURN_GUIDE>")
        
        if 'difficulty_guide' in design_docs:
            sections.append(f"<DIFFICULTY_GUIDE>\n{design_docs['difficulty_guide']}\n</DIFFICULTY_GUIDE>")
        
        if 'multiplayer_guide' in design_docs:
            sections.append(f"<MULTIPLAYER_GUIDE>\n{design_docs['multiplayer_guide']}\n</MULTIPLAYER_GUIDE>")
        
        return "\n\n".join(sections)
    
    def get_cache_name(self):
        """Returns the current cache name/identifier."""
        return self.cache_metadata.get('cache_name')
    
    def is_cache_valid(self):
        """Check if the current cache is still valid (not expired)."""
        if not self.cache_metadata or 'expires_at' not in self.cache_metadata:
            return False
        
        expires_at = datetime.fromisoformat(self.cache_metadata['expires_at'])
        return datetime.now() < expires_at
    
    def refresh_cache_if_needed(self, design_docs):
        """
        Checks if cache needs refresh and recreates if expired.
        
        Args:
            design_docs: Dict of design documents (same format as create_design_doc_cache)
        
        Returns:
            Cache name (existing or newly created)
        """
        if self.is_cache_valid():
            print(f"✓ Using existing cache: {self.get_cache_name()}")
            return self.get_cache_name()
        
        print("⟳ Cache expired or invalid, creating new cache...")
        return self.create_design_doc_cache(design_docs)
    
    def invalidate_cache(self):
        """Manually invalidate the cache (e.g., if design docs change)."""
        cache_name = self.get_cache_name()
        
        if cache_name:
            try:
                self.client.caches.delete(name=cache_name)
                print(f"✓ Deleted cache: {cache_name}")
            except Exception as e:
                print(f"⚠ Cache deletion failed: {e}")
        
        # Clear metadata
        self.cache_metadata = {}
        self._save_metadata()
        print("✓ Cache metadata cleared")
