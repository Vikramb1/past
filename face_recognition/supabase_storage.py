"""
Supabase storage integration for uploading detected face images.
"""
import os
from typing import Optional
from supabase import create_client, Client
import config


class SupabaseStorage:
    """Handles uploads to Supabase storage bucket."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.url = config.SUPABASE_URL
        self.key = config.SUPABASE_SERVICE_KEY
        self.bucket_name = config.SUPABASE_BUCKET_NAME
        
        try:
            self.client: Client = create_client(self.url, self.key)
            print(f"✅ Supabase Storage initialized")
            print(f"   URL: {self.url}")
            print(f"   Bucket: {self.bucket_name}")
            
            # Verify bucket exists
            self._verify_bucket()
            
        except Exception as e:
            print(f"❌ Failed to initialize Supabase: {e}")
            self.client = None
    
    def _verify_bucket(self):
        """Verify that the storage bucket exists."""
        try:
            buckets = self.client.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            
            if self.bucket_name not in bucket_names:
                print(f"⚠️  Bucket '{self.bucket_name}' not found")
                print(f"   Available buckets: {bucket_names}")
                print(f"   Creating bucket...")
                
                # Try to create the bucket
                self.client.storage.create_bucket(
                    self.bucket_name,
                    options={"public": False}
                )
                print(f"✅ Bucket '{self.bucket_name}' created")
            else:
                print(f"✅ Bucket '{self.bucket_name}' exists")
                
        except Exception as e:
            print(f"⚠️  Could not verify bucket: {e}")
    
    def upload_face_image(
        self,
        file_path: str,
        storage_path: str
    ) -> Optional[dict]:
        """
        Upload a face image to Supabase storage.
        
        Args:
            file_path: Local file path to upload
            storage_path: Path in Supabase storage (e.g., "faces/person_001_1729881234.png")
        
        Returns:
            Upload response dict or None if failed
        """
        if not self.client:
            print("⚠️  Supabase client not initialized")
            return None
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to Supabase
            response = self.client.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_data,
                file_options={"content-type": "image/png"}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(storage_path)
            
            print(f"✅ Uploaded to Supabase: {storage_path}")
            
            return {
                'success': True,
                'storage_path': storage_path,
                'public_url': public_url,
                'response': response
            }
            
        except Exception as e:
            print(f"❌ Failed to upload to Supabase: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from Supabase storage.
        
        Args:
            storage_path: Path in storage to delete
        
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            self.client.storage.from_(self.bucket_name).remove([storage_path])
            print(f"🗑️  Deleted from Supabase: {storage_path}")
            return True
        except Exception as e:
            print(f"⚠️  Failed to delete: {e}")
            return False
    
    def list_files(self, path: str = "") -> list:
        """
        List files in storage bucket.
        
        Args:
            path: Path prefix to list
        
        Returns:
            List of files
        """
        if not self.client:
            return []
        
        try:
            files = self.client.storage.from_(self.bucket_name).list(path)
            return files
        except Exception as e:
            print(f"⚠️  Failed to list files: {e}")
            return []
    
    def get_public_url(self, storage_path: str) -> Optional[str]:
        """
        Get public URL for a file.
        
        Args:
            storage_path: Path in storage
        
        Returns:
            Public URL or None
        """
        if not self.client:
            return None
        
        try:
            return self.client.storage.from_(self.bucket_name).get_public_url(storage_path)
        except Exception as e:
            print(f"⚠️  Failed to get public URL: {e}")
            return None
    
    def query_face_search(self, image_filename: str) -> Optional[dict]:
        """
        Query face_searches table for a specific image.
        Matches on trigger_image_url containing the filename.
        
        Args:
            image_filename: Image filename to search for (e.g., "person_001_1729901234.png")
        
        Returns:
            Database row as dict or None if not found
        """
        print(f"\n💾 [DEBUG] Querying Supabase for: {image_filename}")
        
        if not self.client:
            print("⚠️  Supabase client not initialized")
            return None
        
        try:
            print(f"   Table: face_searches")
            print(f"   Query: trigger_image_url LIKE '%{image_filename}%'")
            
            response = self.client.table('face_searches') \
                .select('*') \
                .like('trigger_image_url', f'%{image_filename}%') \
                .execute()
            
            print(f"   Results found: {len(response.data) if response.data else 0}")
            
            if response.data and len(response.data) > 0:
                result = response.data[0]
                print(f"   ✅ Found record:")
                print(f"      - ID: {result.get('id', 'N/A')}")
                print(f"      - Full name: {result.get('full_name', 'N/A')}")
                print(f"      - Trigger image URL: {result.get('trigger_image_url', 'N/A')}")
                print(f"      - text_to_display: {bool(result.get('text_to_display'))}")
                if result.get('text_to_display'):
                    preview = result.get('text_to_display', '')[:100]
                    print(f"      - text_to_display preview: {preview}...")
                print(f"      - Social media: {bool(result.get('social_media'))}")
                print(f"      - Nyne AI response: {bool(result.get('nyne_ai_response'))}")
                print(f"      - Google image results: {bool(result.get('google_image_results'))}")
                return result
            else:
                print(f"   ℹ️  No records found")
            return None
        except Exception as e:
            print(f"⚠️  Error querying face_searches: {e}")
            import traceback
            traceback.print_exc()
            return None

