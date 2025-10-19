"""
Google Cloud Storage Handler
"""

import os
import tempfile
from google.cloud import storage


class GCSHandler:
    """Handles file operations with Google Cloud Storage"""
    
    def __init__(self, bucket_name):
        """Initialize GCS client and bucket"""
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
    
    def download_to_local(self, blob_name, local_path=None):
        """
        Download file from GCS to local path
        
        Args:
            blob_name: Name of blob in bucket
            local_path: Optional local path. If None, creates temp file.
            
        Returns:
            Path to local file
        """
        blob = self.bucket.blob(blob_name)
        
        if not local_path:
            # Create temp file with proper extension
            suffix = os.path.splitext(blob_name)[1] or '.m4a'
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            local_path = temp.name
            temp.close()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path) if os.path.dirname(local_path) else '.', exist_ok=True)
        
        blob.download_to_filename(local_path)
        return local_path
    
    def delete_file(self, blob_name):
        """Delete file from GCS bucket"""
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
        except Exception:
            pass
    
    def file_exists(self, blob_name):
        """Check if file exists in bucket"""
        blob = self.bucket.blob(blob_name)
        return blob.exists()
