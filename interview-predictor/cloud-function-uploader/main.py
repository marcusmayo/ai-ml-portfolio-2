"""
Cloud Function for handling large file uploads
"""

import os
import functions_framework
from google.cloud import storage
from flask import jsonify
import hashlib
import time


@functions_framework.http
def upload_file(request):
    """
    HTTP Cloud Function for file uploads
    Handles CORS and file storage to GCS
    """
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Upload-Token',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers for actual request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    # Validate upload token (simple validation)
    token = request.headers.get('X-Upload-Token')
    if not token:
        return (jsonify({'error': 'Missing upload token'}), 401, headers)
    
    # Get bucket name from environment
    bucket_name = os.environ.get('GCS_BUCKET_NAME')
    if not bucket_name:
        return (jsonify({'error': 'Bucket not configured'}), 500, headers)
    
    try:
        # Get uploaded file
        if 'file' not in request.files:
            return (jsonify({'error': 'No file provided'}), 400, headers)
        
        file = request.files['file']
        
        if file.filename == '':
            return (jsonify({'error': 'Empty filename'}), 400, headers)
        
        # Validate file type
        allowed_extensions = {'.mp3', '.wav', '.m4a', '.mp4'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return (jsonify({'error': 'Invalid file type'}), 400, headers)
        
        # Generate unique blob name
        timestamp = int(time.time())
        file_hash = hashlib.md5(f"{file.filename}{timestamp}".encode()).hexdigest()[:8]
        blob_name = f"uploads/{timestamp}_{file_hash}_{file.filename}"
        
        # Upload to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Upload with content type
        content_type = file.content_type or 'audio/mpeg'
        blob.upload_from_file(file, content_type=content_type)
        
        return (jsonify({
            'success': True,
            'blob_name': blob_name,
            'size': blob.size,
            'filename': file.filename
        }), 200, headers)
        
    except Exception as e:
        return (jsonify({'error': str(e)}), 500, headers)
