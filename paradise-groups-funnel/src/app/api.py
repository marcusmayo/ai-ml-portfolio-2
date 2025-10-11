"""
Paradise Groups Funnel API
Lead capture API for Facebook Groups quiz
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sys

# Fix imports to work both locally and in Cloud Run
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import our modules
from models.schemas import QuizSubmission, QuizResponse, Lead
from utils.firestore_client import firestore_client

# Create FastAPI app
app = FastAPI(
    title="Paradise Groups Funnel API",
    description="Lead capture API for Facebook Groups quiz",
    version="0.1.0"
)

# Allow CORS (so React frontend can call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (for Cloud Run)
@app.get("/health")
async def health_check():
    """Check if the API is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("APP_ENV", "unknown")
    }

# Root endpoint
@app.get("/")
async def root():
    """Welcome message"""
    return {
        "message": "Welcome to Paradise Groups Funnel API",
        "docs": "/docs",
        "health": "/health",
        "version": "0.1.0"
    }

# Quiz submission endpoint
@app.post("/api/quiz", response_model=QuizResponse)
async def submit_quiz(submission: QuizSubmission):
    """
    Submit quiz results and save lead to Firestore
    
    This endpoint:
    1. Validates the quiz data
    2. Saves the lead to Firestore
    3. Returns a success message with lead ID
    4. (Future: sends welcome email with itinerary)
    """
    try:
        # Convert submission to dict for Firestore
        lead_data = submission.model_dump()
        
        # Save to Firestore
        lead_id = firestore_client.save_lead(lead_data)
        
        # Create a simple itinerary preview based on vibe
        itinerary_previews = {
            "chill": {
                "day_1": "Morning beach walk, lunch at beachside café, afternoon hammock time, sunset viewing",
                "day_2": "Lazy breakfast, spa treatment, pool lounging, romantic dinner"
            },
            "adventure": {
                "day_1": "Zip-lining at Ocean World, snorkeling at Sosua Bay, seafood lunch, beach volleyball",
                "day_2": "Catamaran sailing, cave exploration, local market tour, live music"
            },
            "music": {
                "day_1": "Beach morning, salsa lessons, lunch with live music, evening bachata dancing",
                "day_2": "Local musician brunch, instrument workshop, concert night"
            },
            "wellness": {
                "day_1": "Sunrise yoga, healthy breakfast, spa morning, meditation, organic lunch",
                "day_2": "Beach walk, wellness workshop, massage, vegetarian dinner"
            },
            "luxe": {
                "day_1": "Private beach cabana, champagne brunch, couples massage, fine dining",
                "day_2": "Private chef breakfast, yacht excursion, VIP lounge, gourmet dinner"
            }
        }
        
        itinerary = itinerary_previews.get(
            submission.vibe, 
            itinerary_previews["chill"]
        )
        
        # Return success response
        return QuizResponse(
            success=True,
            message=f"Thanks! Your {submission.vibe} vibe itinerary is ready. Check your email at {submission.email}.",
            lead_id=lead_id,
            itinerary_preview=itinerary
        )
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error saving lead: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save quiz submission: {str(e)}"
        )

# Get lead by ID (for testing/admin)
@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    """Get a lead by ID (for testing purposes)"""
    lead = firestore_client.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
