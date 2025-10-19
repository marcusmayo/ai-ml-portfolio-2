"""
LangGraph Agent for Goal Planning
Multi-node workflow: Planner → Router → Tools → Evaluator
"""
from typing import Dict, Any, List, TypedDict, Annotated
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
    goal: str                           # User's goal
    user_profile: str                   # User persona (novice/diy/near-retiree)
    analysis: str                       # Planner's analysis
    goal_type: str                      # retirement/home/college/general
    tool_calls: List[Dict[str, Any]]    # API calls made
    api_data: Dict[str, Any]            # Results from tools
    plan_steps: List[Dict[str, Any]]    # Generated plan
    summary: str                        # Plan summary
    confidence_score: float             # 0-1
    eval_pass: bool                     # Evaluation result
    error: str                          # Error message if any

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
1. Classify the goal type: retirement, home_purchase, college_savings, or general
2. Identify key parameters (age, timeline, amounts, etc.)
3. Determine what financial calculations are needed

Respond in JSON format:
{
    "goal_type": "retirement|home_purchase|college_savings|general",
    "analysis": "brief analysis of the goal",
    "parameters": {
        "key": "value pairs extracted from goal"
    },
    "tools_needed": ["retirement_calculator|mortgage_calculator|stock_quote"]
}"""
    
    user_message = f"""Goal: {state['goal']}
User Profile: {state['user_profile']}

Analyze this goal and provide structured output."""
    
    try:
        response = bedrock_client.invoke(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            max_tokens=1000,
            temperature=0.1  # Low temp for consistent classification
        )
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            analysis_data = json.loads(json_match.group())
            state['goal_type'] = analysis_data.get('goal_type', 'general')
            state['analysis'] = analysis_data.get('analysis', '')
            
            logger.info(f"PLANNER: Classified as '{state['goal_type']}'")
        else:
            # Fallback: simple keyword matching
            goal_lower = state['goal'].lower()
            if 'retire' in goal_lower or '401k' in goal_lower or 'pension' in goal_lower:
                state['goal_type'] = 'retirement'
            elif 'home' in goal_lower or 'house' in goal_lower or 'mortgage' in goal_lower:
                state['goal_type'] = 'home_purchase'
            elif 'college' in goal_lower or 'education' in goal_lower or '529' in goal_lower:
                state['goal_type'] = 'college_savings'
            else:
                state['goal_type'] = 'general'
            
            state['analysis'] = f"Goal analysis: {state['goal_type']} planning"
            logger.warning("PLANNER: JSON parsing failed, used keyword fallback")
        
    except Exception as e:
        logger.error(f"PLANNER: Error: {e}")
        state['goal_type'] = 'general'
        state['analysis'] = "Error during analysis"
        state['error'] = str(e)
    
    return state

# ============================================================================
# NODE 2: ROUTER (Decides which tools to call)
# ============================================================================

def router_node(state: AgentState) -> AgentState:
    """
    Route to appropriate financial tools based on goal type
    """

    logger.info(f"ROUTER: Routing '{state['goal_type']}' goal")
    
    state['tool_calls'] = []
    state['api_data'] = {}
    goal_text = (state.get('goal') or '').lower()
    
    try:
        if state['goal_type'] == 'retirement':
            # Call retirement tools
            logger.info("ROUTER: Calling retirement tools")
            
            # Get market data
            quote = get_stock_quote("SPY")
            state['api_data']['stock_quote'] = quote
            state['tool_calls'].append({"tool": "stock_quote", "symbol": "SPY"})
            
            # Calculate projection (use defaults for demo)
            # Extract values from goal using LLM
            import re
            
            # Try to extract monthly contribution from goal
            monthly_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per month|monthly|a month|each month)', goal_text)
            monthly_contribution = float(monthly_match.group(1).replace(',', '')) if monthly_match else 500
            
            # Try to extract timeframe (years)
            years_match = re.search(r'(?:in|for|over)\s+(\d+)\s+years?', goal_text)
            years = int(years_match.group(1)) if years_match else 35
            
            # Try to extract current savings
            savings_match = re.search(r'(?:have|saved|current(?:ly)?)\s+\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', goal_text)
            current_savings = float(savings_match.group(1).replace(',', '')) if savings_match else 0
            
            # Calculate ages
            current_age = 30  # Default assumption
            retirement_age = current_age + years
            
            # Extract parameters from user's goal
            
            # Extract monthly contribution (e.g., '$500 per month')
            monthly_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per month|/month|monthly|a month|each month)', goal_text)
            monthly_contribution = float(monthly_match.group(1).replace(',', '')) if monthly_match else 500
            
            # Extract timeframe in years (e.g., 'in 20 years')
            years_match = re.search(r'(?:in|for|over)\s+(\d+)\s+years?', goal_text)
            years = int(years_match.group(1)) if years_match else 30
            
            # Extract current savings if mentioned
            savings_match = re.search(r'(?:have|saved|starting with|current(?:ly)?)\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', goal_text)
            current_savings = float(savings_match.group(1).replace(',', '')) if savings_match else 0
            
            # Calculate ages
            current_age = 30  # Default assumption
            retirement_age = current_age + years
            
            logger.info(f"EXTRACTED: monthly=${monthly_contribution}, years={years}, current_savings=${current_savings}")
            
            projection = calculate_retirement_projection(
                current_age=current_age,
                retirement_age=retirement_age,
                monthly_contribution=monthly_contribution,
                current_savings=current_savings
            )
            state['api_data']['retirement_projection'] = projection
            state['tool_calls'].append({"tool": "retirement_calculator"})
            
        elif state['goal_type'] == 'home_purchase':
            # Call mortgage calculator
            logger.info("ROUTER: Calling mortgage calculator")
            
            mortgage = calculate_mortgage(
                home_price=500000,
                down_payment_percent=20,
                interest_rate=7.0,
                loan_term_years=30
            )
            state['api_data']['mortgage'] = mortgage
            state['tool_calls'].append({"tool": "mortgage_calculator"})
            
        elif state['goal_type'] == 'college_savings':
            # Use retirement calculator with different parameters
            logger.info("ROUTER: Calling college savings calculator")
            
            projection = calculate_retirement_projection(
                current_age=0,  # Child's age
                retirement_age=18,  # College age
                monthly_contribution=300,
                current_savings=5000,
                expected_return=0.06
            )
            state['api_data']['college_projection'] = projection
            state['tool_calls'].append({"tool": "college_calculator"})
        
        else:
            # General advice - get market overview
            logger.info("ROUTER: General financial overview")
            quote = get_stock_quote("SPY")
            state['api_data']['market_overview'] = quote
            state['tool_calls'].append({"tool": "market_overview"})
        
        logger.info(f"ROUTER: Called {len(state['tool_calls'])} tools")
        
    except Exception as e:
        logger.error(f"ROUTER: Error calling tools: {e}")
        state['error'] = str(e)
    
    return state

# ============================================================================
# NODE 3: PLAN GENERATOR (Uses Claude to create structured plan)
# ============================================================================

def plan_generator_node(state: AgentState) -> AgentState:
    """
    Generate structured financial plan using API data
    """
    logger.info("PLAN GENERATOR: Creating plan with API data")
    
    system_prompt = """You are a financial planning expert. Create a detailed, actionable plan.

Use the provided API data to make your plan specific and realistic.
Structure your response as a numbered list of steps with:
- Step number and title
- Detailed description
- Estimated timeline
- Resources needed

Be specific, cite numbers from the API data, and make it actionable."""
    
    api_data_str = json.dumps(state['api_data'], indent=2)
    
    user_message = f"""Goal: {state['goal']}
User Profile: {state['user_profile']}
Goal Type: {state['goal_type']}
Analysis: {state['analysis']}

API Data:
{api_data_str}

Create a detailed, step-by-step financial plan."""
    
    try:
        response = bedrock_client.invoke(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            max_tokens=2000,
            temperature=0.3
        )
        
        # Parse steps from response
        steps = []
        lines = response.split('\n')
        current_step = {}
        step_number = 1
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('Step')):
                # New step
                if current_step:
                    steps.append(current_step)
                current_step = {
                    "step_number": step_number,
                    "title": line.split('.', 1)[-1].strip()[:100],
                    "description": "",
                    "estimated_duration": "1-2 weeks",
                    "resources_needed": []
                }
                step_number += 1
            elif current_step and line:
                current_step['description'] += line + " "
        
        if current_step:
            steps.append(current_step)
        
        # Clean up descriptions
        for step in steps:
            step['description'] = step['description'].strip()[:500]
        
        state['plan_steps'] = steps if steps else [
            {
                "step_number": 1,
                "title": "Review Generated Plan",
                "description": response[:500],
                "estimated_duration": "Review carefully",
                "resources_needed": ["Financial advisor"]
            }
        ]
        
        # Generate summary
        summary_parts = [f"Plan for: {state['goal']}"]
        if state['goal_type'] == 'retirement' and 'retirement_projection' in state['api_data']:
            proj = state['api_data']['retirement_projection']
            summary_parts.append(
                f"Projected retirement savings: ${proj['projected_balance']:,.2f}"
            )
        elif state['goal_type'] == 'home_purchase' and 'mortgage' in state['api_data']:
            mort = state['api_data']['mortgage']
            summary_parts.append(
                f"Monthly payment estimate: ${mort['total_monthly_payment']:,.2f}"
            )
        
        summary_parts.append(f"{len(steps)} actionable steps provided.")
        state['summary'] = " | ".join(summary_parts)
        
        logger.info(f"PLAN GENERATOR: Created {len(steps)} steps")
        
    except Exception as e:
        logger.error(f"PLAN GENERATOR: Error: {e}")
        state['error'] = str(e)
        state['plan_steps'] = []
        state['summary'] = "Error generating plan"
    
    return state

# ============================================================================
# NODE 4: EVALUATOR (Validates plan quality)
# ============================================================================

def evaluator_node(state: AgentState) -> AgentState:
    """
    Evaluate plan quality and assign confidence score
    """
    logger.info("EVALUATOR: Validating plan")
    
    checks_passed = 0
    total_checks = 5
    
    # Check 1: Has steps
    if len(state['plan_steps']) >= 2:
        checks_passed += 1
        logger.debug("✓ Plan has multiple steps")
    
    # Check 2: Has API data
    if state['api_data']:
        checks_passed += 1
        logger.debug("✓ API data included")
    
    # Check 3: Steps have descriptions
    if all(step.get('description') for step in state['plan_steps']):
        checks_passed += 1
        logger.debug("✓ All steps have descriptions")
    
    # Check 4: Has summary
    if state['summary'] and len(state['summary']) > 20:
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
