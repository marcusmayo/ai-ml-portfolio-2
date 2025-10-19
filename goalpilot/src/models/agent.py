"""
LangGraph Agent for Goal Planning
Multi-node workflow: Planner → Router → Plan Generator → Evaluator
"""
from typing import Dict, Any, List, TypedDict
from datetime import datetime
import json
import re

from langgraph.graph import StateGraph, END
from src.models.bedrock_client import bedrock_client
from src.features.alpha_vantage_tool import (
    get_stock_quote, 
    calculate_retirement_projection
)
from src.features.mortgage_tool import calculate_mortgage
from src.utils.logger import logger

# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """State passed between agent nodes"""
    goal: str
    user_profile: str
    analysis: str
    goal_type: str
    tool_calls: List[Dict[str, Any]]
    api_data: Dict[str, Any]
    plan_steps: List[Dict[str, Any]]
    summary: str
    confidence_score: float
    eval_pass: bool
    error: str


# ============================================================================
# NODE 1: PLANNER (Uses Claude to analyze goal)
# ============================================================================

def planner_node(state: AgentState) -> AgentState:
    """
    Analyze user goal and determine what needs to be done
    Uses Claude to understand intent and classify goal type
    """
    logger.info(f"PLANNER: Analyzing goal: {state['goal']}")
    
    system_prompt = """You are a financial planning assistant. Analyze the user's goal and:
1. Classify the goal type (retirement/home_purchase/college/debt/general)
2. Identify key parameters and timeline
3. Determine which financial tools are needed
4. Provide initial analysis

Return a JSON object with:
{
    "goal_type": "retirement|home_purchase|college|debt|general",
    "analysis": "brief analysis of the goal",
    "parameters": {key parameters extracted},
    "tools_needed": ["tool1", "tool2"]
}"""

    user_message = f"""Goal: {state['goal']}
User Profile: {state['user_profile']}

Analyze this financial goal and provide structured output."""

    try:
        response = bedrock_client.invoke(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            max_tokens=1000,
            temperature=0.2
        )
        
        # Parse JSON response
        result = json.loads(response)
        
        state['goal_type'] = result.get('goal_type', 'general')
        state['analysis'] = result.get('analysis', '')
        
        logger.info(f"PLANNER: Classified as '{state['goal_type']}'")
        return state
        
    except Exception as e:
        logger.error(f"Planner error: {e}")
        state['error'] = f"Planning failed: {str(e)}"
        return state

# ============================================================================
# NODE 2: ROUTER (Calls appropriate financial APIs)
# ============================================================================

def router_node(state: AgentState) -> AgentState:
    """
    Route to appropriate financial tools based on goal type
    Calls APIs and stores results in state
    """
    logger.info(f"ROUTER: Routing '{state['goal_type']}' goal")
    
    tool_calls = []
    api_data = {}
    
    try:
        goal_type = state['goal_type']
        
        # Retirement goals
        if goal_type == 'retirement':
            logger.info("ROUTER: Calling retirement tools")
            
            # Get market data
            spy_quote = get_stock_quote('SPY')
            tool_calls.append({"tool": "get_stock_quote", "params": {"symbol": "SPY"}})
            api_data['spy_quote'] = spy_quote
            
            # Calculate retirement projection
            retirement_data = calculate_retirement_projection(
                current_age=30,
                retirement_age=65,
                monthly_contribution=500,
                current_savings=10000
            )
            tool_calls.append({"tool": "retirement_projection", "params": retirement_data})
            api_data['retirement_projection'] = retirement_data
            
        # Home purchase goals
        elif goal_type == 'home_purchase':
            logger.info("ROUTER: Calling mortgage calculator")
            
            mortgage_data = calculate_mortgage(
                home_price=400000,
                down_payment_percent=20,
                interest_rate=7.0,
                loan_term_years=30
            )
            tool_calls.append({"tool": "mortgage_calculator", "params": mortgage_data})
            api_data['mortgage'] = mortgage_data
            
        # General financial goals
        else:
            logger.info("ROUTER: Using market overview")
            spy_quote = get_stock_quote('SPY')
            tool_calls.append({"tool": "get_stock_quote", "params": {"symbol": "SPY"}})
            api_data['market_data'] = spy_quote
        
        state['tool_calls'] = tool_calls
        state['api_data'] = api_data
        
        logger.info(f"ROUTER: Called {len(tool_calls)} tools")
        return state
        
    except Exception as e:
        logger.error(f"Router error: {e}")
        state['error'] = f"Routing failed: {str(e)}"
        return state


# ============================================================================
# NODE 3: PLAN GENERATOR (Creates detailed action plan)
# ============================================================================

def plan_generator_node(state: AgentState) -> AgentState:
    """
    Build the user-facing plan (summary + plan_steps) using API data and/or model output.
    Priority order:
      1) Well-formed JSON (dict or JSON string) with `plan_steps`
      2) Extract JSON from text that contains a JSON block
      3) Fallback line-based parsing from plain text
    Never overwrite non-empty plan_steps with empty results.
    """
    logger.info("PLAN GENERATOR: Creating plan with API data")
    
    # Helper function to normalize step keys
    def _coerce_step(d: Dict[str, Any], idx: int) -> Dict[str, Any]:
        """Normalize different step key variants"""
        return {
            "step_number": d.get("step_number") or d.get("step") or idx,
            "title": d.get("title") or d.get("action") or d.get("step_title") or f"Step {idx}",
            "description": d.get("description") or d.get("details") or d.get("step_description") or "",
            "estimated_duration": d.get("estimated_duration") or d.get("timeline") or d.get("duration") or "TBD",
            "resources_needed": d.get("resources_needed") or d.get("resources") or []
        }
    
    # Helper function to extract JSON from mixed text
    def _extract_json_from_text(text: str) -> Any:
        """Extract JSON object or array from text that may contain other content"""
        patterns = [
            r'\{[^{}]*"plan_steps"[^{}]*\[[^\]]*\][^{}]*\}',  # Object with plan_steps array
            r'\[[^\[\]]*\{[^\}]*"step_number"[^\}]*\}[^\[\]]*\]',  # Array of step objects
            r'\{(?:[^{}]|\{[^{}]*\})*\}',  # Any JSON object
            r'\[(?:[^\[\]]|\[[^\[\]]*\])*\]'  # Any JSON array
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    continue
        return None
    
    # Helper function to parse line-based format
    def _parse_line_based(text: str) -> List[Dict[str, Any]]:
        """Parse steps from numbered list format"""
        steps = []
        lines = text.strip().split('\n')
        current_step = None
        
        for line in lines:
            line = line.strip()
            # Match: "1. Title" or "Step 1: Title"
            match = re.match(r'^(?:Step\s+)?(\d+)[\.:)\s]+(.+)$', line, re.IGNORECASE)
            if match:
                if current_step:
                    steps.append(current_step)
                current_step = {
                    "step_number": int(match.group(1)),
                    "title": match.group(2).strip(),
                    "description": "",
                    "estimated_duration": "TBD",
                    "resources_needed": []
                }
            elif current_step and line:
                current_step["description"] += " " + line
        
        if current_step:
            steps.append(current_step)
        
        return steps
    
    try:
        # Build context for the LLM
        api_context = json.dumps(state['api_data'], indent=2) if state['api_data'] else "No API data available"
        
        system_prompt = """You are a financial planning assistant. Create a detailed, actionable plan with 10-15 specific steps.

Return ONLY a JSON object in this exact format:
{
    "summary": "Brief overview of the plan",
    "plan_steps": [
        {
            "step_number": 1,
            "title": "Clear action title",
            "description": "Detailed explanation of what to do and why",
            "estimated_duration": "Time to complete",
            "resources_needed": ["Resource 1", "Resource 2"]
        }
    ]
}

Each step must be:
- Specific and actionable
- Include clear description
- Have realistic timeline
- List concrete resources"""

        user_message = f"""Goal: {state['goal']}
User Profile: {state['user_profile']}
Goal Type: {state['goal_type']}
Analysis: {state['analysis']}

Financial Data Available:
{api_context}

Create a comprehensive financial plan with 10-15 actionable steps."""

        response = bedrock_client.invoke(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            max_tokens=3000,
            temperature=0.3
        )
        
        parsed_steps = []
        
        # Try parsing response as direct JSON
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "plan_steps" in data:
                parsed_steps = [_coerce_step(s, i+1) for i, s in enumerate(data["plan_steps"])]
                state['summary'] = data.get('summary', '')
            elif isinstance(data, list):
                parsed_steps = [_coerce_step(s, i+1) for i, s in enumerate(data)]
        except json.JSONDecodeError:
            # Try extracting JSON from text
            extracted = _extract_json_from_text(response)
            if extracted:
                if isinstance(extracted, dict) and "plan_steps" in extracted:
                    parsed_steps = [_coerce_step(s, i+1) for i, s in enumerate(extracted["plan_steps"])]
                    state['summary'] = extracted.get('summary', '')
                elif isinstance(extracted, list):
                    parsed_steps = [_coerce_step(s, i+1) for i, s in enumerate(extracted)]
            else:
                # Fallback to line-based parsing
                parsed_steps = _parse_line_based(response)
        
        # Only update if we got steps
        if parsed_steps:
            state['plan_steps'] = parsed_steps
            logger.info(f"PLAN GENERATOR: Created {len(parsed_steps)} steps")
        else:
            logger.warning("PLAN GENERATOR: No steps parsed, keeping existing steps")
        
        return state
        
    except Exception as e:
        logger.error(f"Plan generator error: {e}")
        state['error'] = f"Plan generation failed: {str(e)}"
        return state


# ============================================================================
# NODE 4: EVALUATOR (Validates plan quality)
# ============================================================================

def evaluator_node(state: AgentState) -> AgentState:
    """
    Evaluate the generated plan for quality and completeness
    Checks 5 criteria and assigns confidence score
    """
    logger.info("EVALUATOR: Validating plan quality")
    
    checks_passed = 0
    total_checks = 5
    
    # Check 1: Has plan steps
    if state.get('plan_steps') and len(state['plan_steps']) > 0:
        checks_passed += 1
        logger.debug(f"✓ Plan has {len(state['plan_steps'])} steps")
    
    # Check 2: Steps are detailed enough
    if state.get('plan_steps'):
        avg_desc_length = sum(len(s.get('description', '')) for s in state['plan_steps']) / len(state['plan_steps'])
        if avg_desc_length > 20:
            checks_passed += 1
            logger.debug("✓ Steps have sufficient detail")
    
    # Check 3: Has API data
    if state.get('api_data') and len(state['api_data']) > 0:
        checks_passed += 1
        logger.debug("✓ Plan uses API data")
    
    # Check 4: Has summary
    if state.get('summary') and len(state['summary']) > 10:
        checks_passed += 1
        logger.debug("✓ Plan has summary")
    
    # Check 5: No errors
    if not state.get('error'):
        checks_passed += 1
        logger.debug("✓ No errors during generation")
    
    state['confidence_score'] = checks_passed / total_checks
    state['eval_pass'] = checks_passed >= 3
    
    logger.info(f"EVALUATOR: Score {state['confidence_score']:.2f} ({'PASS' if state['eval_pass'] else 'FAIL'})")
    
    return state

# ============================================================================
# BUILD GRAPH
# ============================================================================

def create_goal_planning_graph():
    """Create the LangGraph workflow"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("router", router_node)
    workflow.add_node("plan_generator", plan_generator_node)
    workflow.add_node("evaluator", evaluator_node)
    
    # Define edges (workflow)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_edge("router", "plan_generator")
    workflow.add_edge("plan_generator", "evaluator")
    workflow.add_edge("evaluator", END)
    
    return workflow.compile()

# Global graph instance
goal_planning_graph = create_goal_planning_graph()

__all__ = ["goal_planning_graph", "AgentState"]
