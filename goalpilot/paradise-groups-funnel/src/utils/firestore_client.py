"""
Firestore client for saving and retrieving leads
"""
from google.cloud import firestore
from datetime import datetime
from typing import Optional
import os

class FirestoreClient:
    """Simple Firestore client for lead management"""
    
    def __init__(self):
        """Initialize Firestore client"""
        # Firestore automatically uses GCP credentials in Cloud Run
        self.db = firestore.Client()
        self.collection_name = os.getenv("FIRESTORE_COLLECTION", "quiz_leads")
    
    def save_lead(self, lead_data: dict) -> str:
        """
        Save a lead to Firestore
        
        Args:
            lead_data: Dictionary with lead information
            
        Returns:
            Document ID of the saved lead
        """
        # Add timestamps
        lead_data["created_at"] = datetime.utcnow()
        lead_data["updated_at"] = datetime.utcnow()
        lead_data["status"] = lead_data.get("status", "new")
        
        # Save to Firestore
        doc_ref = self.db.collection(self.collection_name).document()
        doc_ref.set(lead_data)
        
        return doc_ref.id
    
    def get_lead(self, lead_id: str) -> Optional[dict]:
        """
        Get a lead by ID
        
        Args:
            lead_id: Firestore document ID
            
        Returns:
            Lead data or None if not found
        """
        doc = self.db.collection(self.collection_name).document(lead_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None
    
    def update_lead_status(self, lead_id: str, status: str) -> bool:
        """
        Update lead status (e.g., 'contacted', 'booked')
        
        Args:
            lead_id: Firestore document ID
            status: New status
            
        Returns:
            True if successful
        """
        doc_ref = self.db.collection(self.collection_name).document(lead_id)
        doc_ref.update({
            "status": status,
            "updated_at": datetime.utcnow()
        })
        return True

# Create a global instance (reused across requests)
firestore_client = FirestoreClient()
