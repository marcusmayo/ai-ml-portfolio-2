from flask import Flask, request, jsonify, render_template
from google.cloud import vision
import io
import base64
import os
from werkzeug.utils import secure_filename
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Google Cloud Vision client
vision_client = vision.ImageAnnotatorClient()

@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "axon-evidence-search"})

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """
    Analyze an uploaded image for objects, text, and other evidence
    
    This is like having an AI detective look at a photo and tell you
    everything it sees - cars, people, license plates, signs, etc.
    """
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read the image file
        image_data = file.read()
        image = vision.Image(content=image_data)
        
        # Perform different types of analysis
        results = {}
        
        # 1. Object Detection - Find cars, people, etc.
        logger.info("Detecting objects in image...")
        objects = vision_client.object_localization(image=image).localized_object_annotations
        results['objects'] = []
        for obj in objects:
            results['objects'].append({
                'name': obj.name,
                'confidence': round(obj.score * 100, 2),
                'coordinates': {
                    'x1': round(obj.bounding_poly.normalized_vertices[0].x * 100, 2),
                    'y1': round(obj.bounding_poly.normalized_vertices[0].y * 100, 2),
                    'x2': round(obj.bounding_poly.normalized_vertices[2].x * 100, 2),
                    'y2': round(obj.bounding_poly.normalized_vertices[2].y * 100, 2)
                }
            })
        
        # 2. Text Detection - Find license plates, signs, etc.
        logger.info("Detecting text in image...")
        texts = vision_client.text_detection(image=image).text_annotations
        results['text_found'] = []
        if texts:
            # First result is the full text, others are individual words
            full_text = texts[0].description if texts else ""
            results['full_text'] = full_text
            
            # Extract individual text elements (could be license plates, signs)
            for text in texts[1:]:  # Skip the first one (full text)
                if len(text.description.strip()) > 1:  # Only meaningful text
                    results['text_found'].append({
                        'text': text.description,
                        'coordinates': {
                            'x1': text.bounding_poly.vertices[0].x,
                            'y1': text.bounding_poly.vertices[0].y,
                            'x2': text.bounding_poly.vertices[2].x,
                            'y2': text.bounding_poly.vertices[2].y
                        }
                    })
        
        # 3. Face Detection - Find people (anonymized for privacy)
        logger.info("Detecting faces in image...")
        faces = vision_client.face_detection(image=image).face_annotations
        results['faces_detected'] = len(faces)
        results['faces'] = []
        for face in faces:
            results['faces'].append({
                'confidence': round(face.detection_confidence * 100, 2),
                'emotions': {
                    'joy': face.joy_likelihood.name,
                    'anger': face.anger_likelihood.name,
                    'surprise': face.surprise_likelihood.name
                }
            })
        
        # 4. Safety Detection - Check for inappropriate content
        logger.info("Checking image safety...")
        safe = vision_client.safe_search_detection(image=image).safe_search_annotation
        results['safety'] = {
            'adult_content': safe.adult.name,
            'violence': safe.violence.name,
            'racy': safe.racy.name
        }
        
        # Create a summary for easy understanding
        summary = f"Found {len(results['objects'])} objects, {len(results['text_found'])} text elements, {results['faces_detected']} faces"
        results['summary'] = summary
        
        logger.info(f"Analysis complete: {summary}")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return jsonify({"error": f"Failed to analyze image: {str(e)}"}), 500

@app.route('/search', methods=['POST'])
def search_evidence():
    """
    Search for specific evidence in analyzed results
    
    For example: "Find all images with red cars and Pennsylvania license plates"
    """
    try:
        data = request.get_json()
        search_query = data.get('query', '').lower()
        
        # Mock Evidence Database - In production, this would be a real database
        # This simulates a database of previously analyzed evidence
        evidence_database = [
            {
                'image_id': 'bodycam_001.jpg',
                'objects_found': ['Car', 'License plate', 'Person'],
                'text_found': ['PA ABC-123', 'STOP'],
                'colors': ['red', 'white'],
                'confidence': 94.2,
                'timestamp': '2024-01-15 14:30:22',
                'location': 'Pennsylvania Ave & 5th St',
                'officer': 'Officer Johnson'
            },
            {
                'image_id': 'dashcam_002.jpg',
                'objects_found': ['Person', 'Hoodie', 'Backpack'],
                'text_found': ['ONE WAY'],
                'colors': ['red', 'black'],
                'confidence': 87.5,
                'timestamp': '2024-01-15 15:45:10',
                'location': 'Main St & Oak Ave',
                'officer': 'Officer Smith'
            },
            {
                'image_id': 'security_003.jpg',
                'objects_found': ['Car', 'License plate', 'Building'],
                'text_found': ['NY XYZ-789', 'PARKING'],
                'colors': ['blue', 'white'],
                'confidence': 91.8,
                'timestamp': '2024-01-15 16:20:33',
                'location': 'Downtown Plaza',
                'officer': 'Officer Davis'
            },
            {
                'image_id': 'bodycam_004.jpg',
                'objects_found': ['Person', 'Vehicle', 'Street sign'],
                'text_found': ['PENNSYLVANIA', 'DEF-456'],
                'colors': ['black', 'yellow'],
                'confidence': 89.3,
                'timestamp': '2024-01-16 09:15:44',
                'location': 'Pennsylvania District',
                'officer': 'Officer Wilson'
            },
            {
                'image_id': 'traffic_005.jpg',
                'objects_found': ['Car', 'Traffic light', 'Person'],
                'text_found': ['SPEED LIMIT 25'],
                'colors': ['red', 'green'],
                'confidence': 93.7,
                'timestamp': '2024-01-16 12:05:18',
                'location': '1st Ave Traffic Cam',
                'officer': 'Automated System'
            }
        ]
        
        # Smart search logic - matches partial terms and synonyms
        mock_results = []
        search_terms = search_query.split()
        
        for evidence in evidence_database:
            match_score = 0
            matched_reasons = []
            
            # Search in objects
            for term in search_terms:
                for obj in evidence['objects_found']:
                    if term in obj.lower():
                        match_score += 10
                        matched_reasons.append(f"Object: {obj}")
                
                # Search in text found
                for text in evidence['text_found']:
                    if term in text.lower():
                        match_score += 15
                        matched_reasons.append(f"Text: {text}")
                
                # Search in colors
                for color in evidence['colors']:
                    if term in color.lower():
                        match_score += 8
                        matched_reasons.append(f"Color: {color}")
                
                # Search in location
                if term in evidence['location'].lower():
                    match_score += 5
                    matched_reasons.append(f"Location: {evidence['location']}")
                
                # Search in image_id (NEW - this was missing!)
                if term in evidence['image_id'].lower():
                    match_score += 12
                    matched_reasons.append(f"Image ID: {evidence['image_id']}")
                
                # Search in officer name (NEW - this was missing!)
                if term in evidence['officer'].lower():
                    match_score += 10
                    matched_reasons.append(f"Officer: {evidence['officer']}")
            
            # Special keyword matching and synonyms
            if any(word in search_query for word in ['pennsylvania', 'pa']):
                if 'PA' in ' '.join(evidence['text_found']) or 'pennsylvania' in evidence['location'].lower():
                    match_score += 20
                    matched_reasons.append("Pennsylvania match")
            
            if 'license' in search_query or 'plate' in search_query:
                if 'License plate' in evidence['objects_found']:
                    match_score += 15
                    matched_reasons.append("License plate detected")
            
            if 'hoodie' in search_query:
                if 'Hoodie' in evidence['objects_found']:
                    match_score += 15
                    matched_reasons.append("Hoodie detected")
            
            # Handle "people" vs "Person" (NEW)
            if 'people' in search_query:
                if 'Person' in evidence['objects_found']:
                    match_score += 10
                    matched_reasons.append("Person detected")
            
            # Handle officer name variations (NEW)
            if 'johnson' in search_query:
                if 'johnson' in evidence['officer'].lower():
                    match_score += 15
                    matched_reasons.append("Officer Johnson match")
            
            if 'davis' in search_query:
                if 'davis' in evidence['officer'].lower():
                    match_score += 15
                    matched_reasons.append("Officer Davis match")
            
            if 'smith' in search_query:
                if 'smith' in evidence['officer'].lower():
                    match_score += 15
                    matched_reasons.append("Officer Smith match")
            
            if 'wilson' in search_query:
                if 'wilson' in evidence['officer'].lower():
                    match_score += 15
                    matched_reasons.append("Officer Wilson match")
            
            # If we have a good match, add to results
            if match_score > 5:
                result = evidence.copy()
                result['match_score'] = match_score
                result['match_reasons'] = matched_reasons
                mock_results.append(result)
        
        # Sort by match score (best matches first)
        mock_results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Limit to top 5 results
        mock_results = mock_results[:5]
        
        return jsonify({
            'query': search_query,
            'results_found': len(mock_results),
            'results': mock_results
        })
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Run the app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
