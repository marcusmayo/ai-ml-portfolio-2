"""
FastAPI application for GoalPilot
Provides HTTP endpoints for AI-powered financial planning
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn

from src.models.agent import goal_planning_graph
from src.utils.logger import logger
from src.utils.config import settings

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="GoalPilot API",
    description="AI-powered financial planning assistant",
    version="1.0.0"
)

# CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request/Response Models
# ============================================================================

class PlanRequest(BaseModel):
    """Request to generate a financial plan"""
    goal: str = Field(..., description="User's financial goal", min_length=10, max_length=500)
    user_profile: str = Field(default="novice", description="User expertise level")

class PlanStep(BaseModel):
    """A single step in the financial plan"""
    step_number: int
    title: str
    description: str
    estimated_duration: Optional[str] = None
    resources_needed: Optional[List[str]] = None

class PlanResponse(BaseModel):
    """Response containing the generated plan"""
    plan_steps: List[PlanStep]
    summary: str
    financial_data: Dict[str, Any]
    sources: List[str]

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "bedrock_model": settings.bedrock_model
    }

@app.post("/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    """Generate a financial plan using the LangGraph agent"""
    logger.info(f"Plan requested: {request.goal}")
    
    try:
        # Prepare agent state
        initial_state = {
            "goal": request.goal,
            "user_profile": request.user_profile,
            "goal_type": "general",
            "analysis": "",
            "tool_calls": [],
            "api_data": {},
            "plan_steps": [],
            "summary": "",
            "confidence_score": 0.0,
            "eval_pass": False,
            "error": ""
        }
        
        # Run the agent
        result = goal_planning_graph.invoke(initial_state)
        
        # Check for errors
        if result.get('error'):
            logger.error(f"Agent error: {result['error']}")
            raise HTTPException(status_code=500, detail=f"Plan generation failed: {result['error']}")
        
        # Convert plan steps to Pydantic models
        plan_steps = [
            PlanStep(
                step_number=step['step_number'],
                title=step['title'],
                description=step['description'],
                estimated_duration=step.get('estimated_duration'),
                resources_needed=step.get('resources_needed', [])
            )
            for step in result.get('plan_steps', [])
        ]
        
        return PlanResponse(
            plan_steps=plan_steps,
            summary=result.get('summary', ''),
            financial_data=result.get('api_data', {}),
            sources=[str(call) for call in result.get('tool_calls', [])]
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting GoalPilot API on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
