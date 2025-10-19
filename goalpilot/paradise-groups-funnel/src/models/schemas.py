"""
Data models for Paradise Groups Funnel
Using Pydantic for validation and type safety
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

# Quiz submission from the user
class QuizSubmission(BaseModel):
    """Data collected from the quiz form"""
    
    # Contact info
    email: EmailStr = Field(..., description="User's email address")
    whatsapp: Optional[str] = Field(None, description="WhatsApp number (optional)")
    
    # Travel preferences
    vibe: Literal["chill", "adventure", "music", "wellness", "luxe"] = Field(
        ..., 
        description="Travel vibe preference"
    )
    travel_month: Optional[str] = Field(None, description="Planned travel month")
    interests: list[str] = Field(
        default_factory=list,
        description="List of interests (beach, food, music, adventure, wellness)"
    )
    budget: Optional[Literal["budget", "moderate", "luxury"]] = Field(
        None,
        description="Budget range"
    )
    
    # Tracking (from Facebook group)
    utm_source: Optional[str] = Field(None, description="Traffic source (fb_group)")
    utm_medium: Optional[str] = Field(None, description="Traffic medium (organic)")
    utm_campaign: Optional[str] = Field(None, description="Campaign name (group name)")
    group_code: Optional[str] = Field(None, description="Group-specific promo code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "traveler@example.com",
                "whatsapp": "+18095551234",
                "vibe": "chill",
                "travel_month": "March",
                "interests": ["beach", "food"],
                "budget": "moderate",
                "utm_source": "fb_group",
                "utm_medium": "organic",
                "utm_campaign": "black_travel_lovers",
                "group_code": "PARA-SUNSET-BTL"
            }
        }


# Saved lead in Firestore (includes timestamps and system fields)
class Lead(BaseModel):
    """Lead record stored in Firestore"""
    
    id: Optional[str] = Field(None, description="Firestore document ID")
    email: EmailStr
    whatsapp: Optional[str] = None
    vibe: str
    travel_month: Optional[str] = None
    interests: list[str] = []
    budget: Optional[str] = None
    
    # Tracking
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    group_code: Optional[str] = None
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="new", description="Lead status (new, contacted, booked)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123xyz",
                "email": "traveler@example.com",
                "whatsapp": "+18095551234",
                "vibe": "chill",
                "travel_month": "March",
                "interests": ["beach", "food"],
                "budget": "moderate",
                "utm_source": "fb_group",
                "utm_campaign": "black_travel_lovers",
                "status": "new",
                "created_at": "2025-10-11T14:30:00Z"
            }
        }


# API response after quiz submission
class QuizResponse(BaseModel):
    """Response sent back to the user"""
    
    success: bool
    message: str
    lead_id: Optional[str] = None
    itinerary_preview: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Thanks! Check your email for your custom Costambar itinerary.",
                "lead_id": "abc123xyz",
                "itinerary_preview": {
                    "day_1": "Beach morning, lunch at local spot, sunset at Playa Dorada",
                    "day_2": "Ocean World adventure, seafood dinner, live music night"
                }
            }
        }
