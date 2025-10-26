"""
Person information API module.
Fetches data from Supabase face_searches table and displays text_to_display field.
"""
import time
import threading
from dataclasses import dataclass
from typing import Dict, Optional
import config
import ollama


@dataclass
class PersonInfo:
    """Person information from Supabase."""
    person_id: str
    status: str  # "scraping", "completed", "error"
    summary: str = ""  # Display text from text_to_display column
    full_name: str = ""  # Store for reference
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'person_id': self.person_id,
            'status': self.status,
            'summary': self.summary,
            'full_name': self.full_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PersonInfo':
        """Create PersonInfo from dictionary."""
        return cls(
            person_id=data.get('person_id', ''),
            status=data.get('status', 'scraping'),
            summary=data.get('summary', ''),
            full_name=data.get('full_name', '')
        )


class PersonInfoAPI:
    """API for fetching and displaying person information from Supabase."""
    
    def __init__(self, face_tracker=None):
        """Initialize the person info API.
        
        Args:
            face_tracker: Optional FaceTracker instance to update with polling results
        """
        self._cache = {}  # Cache PersonInfo objects
        self._llm_cache = {}  # Cache LLM summaries to avoid regenerating
        self._polling_active = {}  # Track active polling threads
        self._supabase_storage = None
        self._face_tracker = face_tracker  # Store reference to update tracker
        
        # Initialize Supabase storage
        if config.ENABLE_SUPABASE_UPLOAD:
            try:
                from supabase_storage import SupabaseStorage
                self._supabase_storage = SupabaseStorage()
                print("✅ Person Info API initialized with Supabase")
            except Exception as e:
                print(f"⚠️  Failed to initialize Supabase for person info: {e}")
        else:
            print("⚠️  Supabase disabled - person info will not be available")
    
    def get_person_info(
        self,
        person_id: str,
        image_filename: Optional[str] = None
    ) -> Optional[PersonInfo]:
        """
        Get person information from Supabase face_searches table.
        
        Args:
            person_id: Unique person identifier
            image_filename: Image filename to match in database (e.g., "person_001_1729901234.png")
        
        Returns:
            PersonInfo object or None if failed
        """
        # Check cache first
        if person_id in self._cache:
            cached = self._cache[person_id]
            # If still scraping and not already polling, start polling
            if cached.status == "scraping" and person_id not in self._polling_active:
                self._start_polling(person_id, image_filename)
            return cached
        
        if not image_filename:
            print(f"⚠️  No image filename provided for {person_id}")
            return None
        
        # Query Supabase
        info = self._fetch_from_supabase(person_id, image_filename)
        
        # Cache the response
        self._cache[person_id] = info
        
        # If scraping, start polling thread
        if info.status == "scraping":
            self._start_polling(person_id, image_filename)
        
        return info
    
    def _fetch_from_supabase(self, person_id: str, image_filename: str) -> PersonInfo:
        """
        Fetch and process person info from Supabase.
        
        Args:
            person_id: Person identifier
            image_filename: Image filename to match
        
        Returns:
            PersonInfo object
        """
        print(f"\n🔍 [DEBUG] Fetching from Supabase for {person_id}")
        print(f"   Image filename: {image_filename}")
        
        if not self._supabase_storage:
            print(f"   ❌ No Supabase storage available")
            return PersonInfo(person_id=person_id, status="error", summary="DB Error")
        
        try:
            # Query database
            result = self._supabase_storage.query_face_search(image_filename)
            
            print(f"   Query result: {result is not None}")
            if result:
                print(f"   Full name: {result.get('full_name', 'N/A')}")
                print(f"   Has text_to_display: {bool(result.get('text_to_display'))}")
                print(f"   Has social_media: {bool(result.get('social_media'))}")
                print(f"   Has nyne_ai_response: {bool(result.get('nyne_ai_response'))}")
            
            if not result:
                # No data found yet
                print(f"   ℹ️  No data in DB yet - still scraping")
                return PersonInfo(
                    person_id=person_id,
                    status="scraping",
                    summary="🔍 Scraping..."
                )
            
            # Parse with LLM
            return self._parse_database_row(person_id, result)
            
        except Exception as e:
            print(f"⚠️  Error fetching person info for {person_id}: {e}")
            import traceback
            traceback.print_exc()
            return PersonInfo(person_id=person_id, status="error", summary="Error")
    
    def _parse_database_row(self, person_id: str, db_row: Dict) -> PersonInfo:
        """
        Parse database row and use text_to_display field directly.
        
        Args:
            person_id: Person identifier
            db_row: Database row with all fields
        
        Returns:
            PersonInfo object
        """
        print(f"\n📊 [DEBUG] Parsing database row for {person_id}")
        
        try:
            full_name = db_row.get('full_name', 'Unknown')
            text_to_display = db_row.get('text_to_display', '')
            has_full_name = bool(db_row.get('full_name'))
            has_text_to_display = bool(text_to_display and text_to_display.strip())
            
            print(f"   Full name: {full_name} (exists: {has_full_name})")
            print(f"   Has text_to_display: {has_text_to_display}")
            if has_text_to_display:
                print(f"   text_to_display preview: {text_to_display[:100]}...")
            
            # Check if we have text_to_display
            if not has_text_to_display:
                # No display text yet - still scraping
                print(f"   ℹ️  No text_to_display yet - marking as scraping")
                return PersonInfo(
                    person_id=person_id,
                    status="scraping",
                    summary="🔍 Scraping data...",
                    full_name=full_name if has_full_name else "Scraping..."
                )
            
            # Use text_to_display directly
            print(f"   ✅ Using text_to_display from database for {person_id}")
            return PersonInfo(
                person_id=person_id,
                status="completed",
                summary=text_to_display,
                full_name=full_name
            )
            
        except Exception as e:
            print(f"⚠️  Error processing data for {person_id}: {e}")
            import traceback
            traceback.print_exc()
            return PersonInfo(
                person_id=person_id,
                status="error",
                summary="❌ Error processing data"
            )
    
    def _generate_llm_summary(self, person_id: str, db_row: Dict) -> str:
        """
        Use Ollama LLM to generate a concise bullet-pointed summary.
        
        Args:
            person_id: Person identifier
            db_row: Database row with all fields
        
        Returns:
            Formatted bullet-pointed summary string
        """
        print(f"\n🤖 [DEBUG] Generating LLM summary for {person_id}")
        
        # Extract available fields
        full_name = db_row.get('full_name', 'Unknown')
        social_media = db_row.get('social_media', {})
        google_images = db_row.get('google_image_results', '')
        nyne_response = db_row.get('nyne_ai_response', {})
        
        print(f"   Input data:")
        print(f"   - Full name: {full_name}")
        print(f"   - Social media keys: {list(social_media.keys()) if isinstance(social_media, dict) else 'N/A'}")
        print(f"   - Google images length: {len(str(google_images))}")
        print(f"   - Nyne response keys: {list(nyne_response.keys()) if isinstance(nyne_response, dict) else 'N/A'}")
        
        # Extract social media links
        social_links = []
        if isinstance(social_media, dict):
            for platform, data in social_media.items():
                if isinstance(data, dict) and 'url' in data:
                    social_links.append(f"{platform}: {data['url']}")
                elif isinstance(data, str) and data.startswith('http'):
                    social_links.append(f"{platform}: {data}")
        
        social_links_str = "\n".join(social_links) if social_links else "None"
        
        # Build context for LLM
        context = f"""
Given this data about {full_name}:
Social Media: {social_links_str}
Additional Info: {nyne_response}

Write 2-3 brief sentences about this person. Include:
- Their profession or role (if known)
- Location (if known)
- One interesting fact (if available)

Rules:
- NO emojis at all
- NO bullet points
- NO markdown formatting
- Plain text sentences only
- Maximum 120 characters total
- If information is missing, don't mention it or use placeholders
- Include social media URLs on separate lines at the end

Example format:
Software Engineer at Google, based in San Francisco.
Specializes in machine learning and AI.
linkedin.com/in/username
twitter.com/username
"""
        
        print(f"\n📝 [DEBUG] LLM Prompt:")
        print(f"   Model: {config.OLLAMA_MODEL}")
        print(f"   Context length: {len(context)} chars")
        print(f"   Context preview: {context[:200]}...")
        
        try:
            print(f"   ⏳ Calling Ollama...")
            # Call Ollama
            response = ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{'role': 'user', 'content': context}]
            )
            
            summary = response['message']['content']
            print(f"   ✅ LLM response received")
            print(f"   Response length: {len(summary)} chars")
            print(f"   Response preview: {summary[:100]}...")
            print(f"✅ LLM summary generated for {person_id}")
            return summary
            
        except Exception as e:
            print(f"⚠️  LLM generation error for {person_id}: {e}")
            import traceback
            traceback.print_exc()
            return f"• {full_name}\n• Error generating summary"
    
    def _start_polling(self, person_id: str, image_filename: str):
        """
        Start background polling thread for a person.
        
        Args:
            person_id: Person to poll for
            image_filename: Image filename to match
        """
        if person_id in self._polling_active and self._polling_active[person_id]:
            return  # Already polling
        
        self._polling_active[person_id] = True
        
        def poll_worker():
            """Background worker that polls for updates."""
            start_time = time.time()
            poll_interval = config.PERSON_INFO_POLL_INTERVAL
            max_poll_time = config.PERSON_INFO_MAX_POLL_TIME
            poll_count = 0
            
            print(f"🔄 [DEBUG] Starting polling for {person_id}...")
            print(f"   Interval: {poll_interval}s, Max time: {max_poll_time}s")
            
            while self._polling_active.get(person_id, False):
                # Check timeout
                if time.time() - start_time > max_poll_time:
                    print(f"⏱️  Polling timeout for {person_id} after {poll_count} attempts")
                    self._polling_active[person_id] = False
                    break
                
                # Wait before next poll
                time.sleep(poll_interval)
                poll_count += 1
                
                try:
                    print(f"\n🔄 [DEBUG] Poll attempt #{poll_count} for {person_id}")
                    # Fetch updated info
                    updated_info = self._fetch_from_supabase(person_id, image_filename)
                    
                    print(f"   Poll result: status={updated_info.status}")
                    
                    # Update cache
                    self._cache[person_id] = updated_info
                    print(f"   ✅ Cache updated for {person_id}")
                    
                    # IMPORTANT: Also update face_tracker if available
                    if self._face_tracker:
                        self._face_tracker.store_api_response(person_id, updated_info.to_dict())
                        print(f"   ✅ Face tracker updated for {person_id}")
                    
                    # If completed or error, stop polling
                    if updated_info.status in ["completed", "error"]:
                        print(f"✅ Person info ready for {person_id}: {updated_info.full_name}")
                        print(f"   Total polls: {poll_count}, Time elapsed: {time.time() - start_time:.1f}s")
                        self._polling_active[person_id] = False
                        break
                    else:
                        print(f"   ℹ️  Still scraping, will poll again in {poll_interval}s")
                        
                except Exception as e:
                    print(f"⚠️  Polling error for {person_id}: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Start thread
        thread = threading.Thread(target=poll_worker, daemon=True)
        thread.start()
    
    def stop_polling(self, person_id: str = None):
        """
        Stop polling for a specific person or all persons.
        
        Args:
            person_id: Person to stop polling for, or None for all
        """
        if person_id:
            self._polling_active[person_id] = False
        else:
            for pid in list(self._polling_active.keys()):
                self._polling_active[pid] = False
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._llm_cache.clear()
        self.stop_polling()
        print("🗑️  Person info cache cleared")


# Singleton instance
_api_instance = None


def get_api_instance(face_tracker=None) -> PersonInfoAPI:
    """Get or create the singleton API instance.
    
    Args:
        face_tracker: Optional FaceTracker instance (only used on first call)
    """
    global _api_instance
    if _api_instance is None:
        _api_instance = PersonInfoAPI(face_tracker=face_tracker)
    return _api_instance
