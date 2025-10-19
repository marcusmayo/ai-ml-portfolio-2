"""
FastAPI application for GoalPilot
Provides HTTP endpoints for AI-powered financial planning
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uvicorn

from src.models.agent import goal_planning_graph
from src.utils.logger import logger
from src.utils.config import settings
from src.monitoring.metrics_tracker import metrics

# Metrics tracking variables
successful_plans = 0
failed_plans = 0
quality_scores: list = []
app_start_time = datetime.now(timezone.utc)

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="GoalPilot API",
    description="AI-powered financial planning assistant",
    version="1.0.0"
)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    global app_start_time
    app_start_time = datetime.now(timezone.utc)
    logger.info("Starting GoalPilot API on port 8000...")


# ============================================================================
# Request/Response Models
# ============================================================================

class PlanRequest(BaseModel):
    """Request to generate a financial plan"""
    goal: str = Field(..., description="User's financial goal", min_length=10, max_length=500)
    user_profile: str = Field(default="novice", description="User expertise level: novice, diy, near-retiree")
    
    class Config:
        json_schema_extra = {
            "example": {
                "goal": "I want to retire comfortably in 20 years",
                "user_profile": "novice"
            }
        }

class PlanStep(BaseModel):
    """A single step in the financial plan"""
    step_number: int
    title: str
    description: str
    estimated_duration: str
    resources_needed: List[str] = []

class PlanResponse(BaseModel):
    """Response containing the generated plan"""
    goal: str
    goal_type: str
    summary: str
    plan_steps: List[PlanStep]
    api_data: Dict[str, Any]
    confidence_score: float
    eval_pass: bool
    timestamp: str
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    bedrock_model: str

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API info"""
    return {
        "message": "GoalPilot API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        bedrock_model=settings.bedrock_model
    )

@app.get("/metrics")
async def get_metrics():
    """Get API usage metrics and OKR progress"""
    try:
        from fastapi.responses import JSONResponse
        
        total_requests = successful_plans + failed_plans
        success_rate = (successful_plans / total_requests * 100) if total_requests > 0 else 0
        avg_quality = (sum(quality_scores) / len(quality_scores)) if quality_scores else 0
        
        goal_total = 100
        progress_percent = round(min(successful_plans / goal_total * 100, 100), 1)
        
        response_data = {
            "status": "success",
            "metrics": {
                "total_requests": total_requests,
                "successful_plans": successful_plans,
                "failed_plans": failed_plans,
                "success_rate_percent": round(success_rate, 2),
                "average_quality_score": round(avg_quality, 2),
                "uptime_since": (app_start_time or datetime.now(timezone.utc)).isoformat(),
            },
            "okr_dashboard": {
                "goal": "Generate 100 successful financial plans",
                "current_progress": successful_plans,
                "progress_percent": progress_percent,
                "quality_target": 0.8,
                "quality_actual": round(avg_quality, 2),
                "status": "on_track" if success_rate > 90 and total_requests > 0 else "needs_attention"
            }
        }
        
        return JSONResponse(content=response_data, status_code=200)
        
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        error_response = {
            "status": "error",
            "error": str(e),
            "metrics": {
                "total_requests": 0,
                "successful_plans": 0,
                "failed_plans": 0,
                "success_rate_percent": 0,
                "average_quality_score": 0,
                "uptime_since": datetime.now(timezone.utc).isoformat(),
            },
            "okr_dashboard": {
                "goal": "Generate 100 successful financial plans",
                "current_progress": 0,
                "progress_percent": 0,
                "quality_target": 0.8,
                "quality_actual": 0,
                "status": "needs_attention"
            }
        }
        return JSONResponse(content=error_response, status_code=500)

@app.post("/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    """
    Generate a financial plan using the AI agent
    
    Args:
        request: PlanRequest with goal and user profile
        
    Returns:
        PlanResponse with generated plan
        
    Raises:
        HTTPException: If plan generation fails
    """
    global successful_plans, failed_plans, quality_scores  # THIS LINE MUST BE HERE
    
    logger.info(f"Plan requested: {request.goal[:50]}...")
    
    try:
        # Prepare agent state
        initial_state = {
            "goal": request.goal,
            "user_profile": request.user_profile,
            "analysis": "",
            "goal_type": "general",
            "tool_calls": [],
            "api_data": {},
            "plan_steps": [],
            "summary": "",
            "confidence_score": 0.0,
            "eval_pass": False,
            "error": ""
        }
        
        # Run the agent
        logger.info("Invoking LangGraph agent...")
        result = goal_planning_graph.invoke(initial_state)
        
        # Check for errors
        if result.get("error"):
            logger.error(f"Agent error: {result['error']}")
            metrics.record_request(success=False)
            raise HTTPException(status_code=500, detail=f"Plan generation failed: {result['error']}")
        
        # Convert plan steps to Pydantic models
        plan_steps = [
            PlanStep(
                step_number=step['step_number'],
                title=step['title'],
                description=step['description'],
                estimated_duration=step.get('estimated_duration', 'TBD'),
                resources_needed=step.get('resources_needed', [])
            )
            for step in result.get('plan_steps', [])
        ]
        
        logger.info(f"Plan generated: {len(plan_steps)} steps")
        
        # Record successful plan
        eval_score = result.get("confidence_score", 1.0)
        metrics.record_request(success=True, eval_score=eval_score)
        
        # Track success metrics
        try:
            global successful_plans, failed_plans, quality_scores
            successful_plans += 1
            conf = result.get("confidence_score", 0)
            if conf and isinstance(conf, (int, float)) and conf > 0:
                quality_scores.append(float(conf))
            logger.info(f"Metrics updated: {successful_plans} successful")
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
        
        # Ensure timestamp is included
        if 'timestamp' not in result:
            result['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        return PlanResponse(**result)
        
    except HTTPException:
        # Track failure for HTTP exceptions
        try:
            failed_plans += 1
        except:
            pass
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        try:
            failed_plans += 1
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/examples", response_model=List[Dict[str, str]])
async def get_examples():
    """Get example goals for testing"""
    return [
        {
            "goal": "I want to retire comfortably in 20 years",
            "user_profile": "novice",
            "description": "Retirement planning for a beginner"
        },
        {
            "goal": "I need to save for a down payment on a $500k house in 5 years",
            "user_profile": "diy",
            "description": "Home purchase planning"
        },
        {
            "goal": "I want to save for my child's college education starting in 18 years",
            "user_profile": "near-retiree",
            "description": "College savings planning"
        }
    ]

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting GoalPilot API on port {settings.api_port}...")
    uvicorn.run(
        "src.app.api:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=True
    )
