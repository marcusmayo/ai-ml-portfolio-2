"""
Streamlit component for direct GCS uploads
"""

import streamlit as st
import streamlit.components.v1 as components


def render_gcs_uploader(signed_url, blob_name):
    """
    Render HTML/JS component for direct GCS upload
    
    Args:
        signed_url: Pre-signed GCS upload URL
        blob_name: Destination blob name
        
    Returns:
        Upload status from JavaScript
    """
    
    upload_html = f"""
    <div id="upload-container">
        <input type="file" id="fileInput" accept=".mp3,.wav,.m4a" 
               style="display:block; margin:10px 0; padding:10px; border:2px solid #4CAF50; border-radius:5px; cursor:pointer;">
        <div id="progress-container" style="display:none; margin:10px 0;">
            <div style="background:#f0f0f0; border-radius:5px; height:30px; position:relative;">
                <div id="progress-bar" style="background:#4CAF50; height:100%; border-radius:5px; width:0%; transition:width 0.3s;"></div>
                <span id="progress-text" style="position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); font-weight:bold;">0%</span>
            </div>
        </div>
        <div id="status" style="margin:10px 0; padding:10px; border-radius:5px;"></div>
    </div>
    
    <script>
    const fileInput = document.getElementById('fileInput');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const statusDiv = document.getElementById('status');
    
    fileInput.addEventListener('change', async (e) => {{
        const file = e.target.files[0];
        if (!file) return;
        
        const fileSizeMB = (file.size / 1024 / 1024).toFixed(1);
        
        statusDiv.textContent = `Uploading ${{file.name}} (${{fileSizeMB}}MB)...`;
        statusDiv.style.background = '#2196F3';
        statusDiv.style.color = 'white';
        progressContainer.style.display = 'block';
        
        try {{
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {{
                if (e.lengthComputable) {{
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBar.style.width = percent + '%';
                    progressText.textContent = percent + '%';
                }}
            }});
            
            xhr.addEventListener('load', () => {{
                if (xhr.status === 200) {{
                    statusDiv.textContent = `✅ Upload complete: ${{file.name}} (${{fileSizeMB}}MB)`;
                    statusDiv.style.background = '#4CAF50';
                    
                    // Signal Streamlit
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        data: {{
                            blob_name: '{blob_name}',
                            filename: file.name,
                            size: file.size,
                            status: 'success'
                        }}
                    }}, '*');
                }} else {{
                    throw new Error(`Upload failed with status ${{xhr.status}}`);
                }}
            }});
            
            xhr.addEventListener('error', () => {{
                statusDiv.textContent = '❌ Upload failed. Please try again.';
                statusDiv.style.background = '#f44336';
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    data: {{ status: 'error' }}
                }}, '*');
            }});
            
            xhr.open('PUT', '{signed_url}', true);
            xhr.setRequestHeader('Content-Type', file.type || 'audio/mpeg');
            xhr.send(file);
            
        }} catch (error) {{
            statusDiv.textContent = '❌ Upload error: ' + error.message;
            statusDiv.style.background = '#f44336';
            statusDiv.style.color = 'white';
        }}
    }});
    </script>
    """
    
    result = components.html(upload_html, height=200)
    return result
