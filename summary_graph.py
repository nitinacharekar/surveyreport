"""
Summary Agent using LangGraph

This module implements a multi-agent system for analyzing and summarizing statistical data.
It uses a graph-based workflow to coordinate multiple agents that process questions,
create summaries, and validate outputs with retry capabilities.

The workflow consists of:
1. Question processing (parallel)
2. Section summarization
3. Persona analysis (parallel)
4. Validation with feedback loop
"""

import os
import json
from pathlib import Path
from statistical_analysis.Section4.section4_full_stats import get_section4_stats
import google.generativeai as genai
import autogen
import concurrent.futures
import re
import logging
from typing import Dict, List, Tuple, Any, Optional, TypedDict
from dataclasses import dataclass
from langgraph.graph import StateGraph, START, END

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('summary_agent.log')
    ]
)
logger = logging.getLogger(__name__)

# Gemini LLM Configuration
GOOGLE_API_KEY = 'AIzaSyASv53dkC5KPaxjNYIpFexVbNmniHp__Hk'
genai.configure(api_key=GOOGLE_API_KEY)

def gemini_llm(prompt: str) -> str:
    """
    Generate a response using the Gemini LLM.
    
    Args:
        prompt: The input prompt for the LLM
        
    Returns:
        The generated text response
    """
    logger.info(f"Generating response for prompt of length {len(prompt)}")
    response = genai.GenerativeModel('models/gemini-1.5-flash').generate_content(prompt)
    logger.debug(f"Generated response: {response.text[:100]}...")
    return response.text

class GeminiAgent(autogen.ConversableAgent):
    """
    Custom agent implementation using Gemini LLM.
    Extends the base ConversableAgent with Gemini-specific functionality.
    """
    
    def __init__(self, name: str, system_message: str):
        """
        Initialize the Gemini agent.
        
        Args:
            name: Unique identifier for the agent
            system_message: The system message defining the agent's role and behavior
        """
        super().__init__(name=name, llm_config=None, system_message=system_message)
        logger.info(f"Initialized GeminiAgent: {name}")
    
    def generate_reply(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a reply using the Gemini LLM.
        
        Args:
            messages: List of message dictionaries containing the conversation history
            
        Returns:
            The generated reply text
        """
        prompt = messages[-1]['content']
        logger.info(f"Agent {self.name} generating reply")
        return gemini_llm(prompt)

# State Management
class AgentState(TypedDict):
    """
    Type definition for the agent state.
    Tracks all necessary information throughout the workflow.
    """
    per_question_outputs: Dict[str, str]  # Question-specific analyses
    section_summary: str                  # Overall section summary
    persona_outputs: Dict[str, str]       # Persona-specific interpretations
    validation: str                       # Current validation result
    validation_feedback: str              # Detailed feedback for improvements
    current_attempt: int                  # Current retry attempt number
    needs_question_rerun: bool           # Flag for question rerun
    needs_section_rerun: bool            # Flag for section rerun

# Node Functions
def process_single_question(q: str, stats: Dict[str, Any], state: AgentState) -> Tuple[str, str]:
    """
    Process a single question with its statistics.
    
    Args:
        q: Question identifier
        stats: Statistics for the question
        state: Current workflow state
        
    Returns:
        Tuple of (question_id, analysis)
    """
    feedback_prompt = ""
    if state['validation_feedback'] and state['needs_question_rerun']:
        feedback_prompt = f"\n\nPrevious validation feedback: {state['validation_feedback']}\nPlease address these issues in your analysis."
    
    agent = GeminiAgent(
        name=f"{q}_agent",
        system_message=f"""You are an expert analyst for {q}. Write a data-grounded summary and analysis of the following statistics. 
        Highlight key trends, outliers, and actionable insights. Do not hallucinate and only output the summary and analysis.
        {feedback_prompt}"""
    )
    prompt = f"Statistics:\n{json.dumps(stats, indent=2)}"
    return q, agent.generate_reply([{'role': 'user', 'content': prompt}])

def process_questions(state: AgentState) -> AgentState:
    """
    Process all questions in parallel.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with question analyses
    """
    logger.info("Processing questions in parallel")
    section4_stats = get_section4_stats()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_question = {
            executor.submit(process_single_question, q, stats, state): q 
            for q, stats in section4_stats.items()
        }
        for future in concurrent.futures.as_completed(future_to_question):
            q, output = future.result()
            state['per_question_outputs'][q] = output
            logger.debug(f"Completed question: {q}")
    
    return state

def process_section(state: AgentState) -> AgentState:
    """
    Process the section summary based on question analyses.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with section summary
    """
    logger.info("Processing section summary")
    feedback_prompt = ""
    if state['validation_feedback'] and state['needs_section_rerun']:
        feedback_prompt = f"\n\nPrevious validation feedback: {state['validation_feedback']}\nPlease address these issues in your synthesis."
    
    section_moderator = GeminiAgent(
        name="section_moderator",
        system_message=f"""You are a Section Moderator. Synthesize the following per-question summaries into 2-3 key insight themes for Section 4. 
        Highlight cross-question patterns and any surprising findings. Do not hallucinate and only output the summary and analysis.
        {feedback_prompt}"""
    )
    section_prompt = "\n\n".join(state['per_question_outputs'].values())
    state['section_summary'] = section_moderator.generate_reply([{'role': 'user', 'content': section_prompt}])
    return state

def process_personas(state: AgentState) -> AgentState:
    """
    Process persona analyses in parallel.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with persona analyses
    """
    logger.info("Processing personas in parallel")
    personas = [
        ("Customer", "You are a customer. Interpret these section insights from your perspective. What stands out? What actions or concerns would you have?"),
        ("Business Customer", "You are a business customer. Interpret these section insights from your perspective. What stands out? What actions or concerns would you have?"),
        ("F5 Vendor", "You are F5 Networks, the vendor. Interpret these section insights from your perspective. What stands out? What actions or concerns would you have?")
    ]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_persona = {
            executor.submit(process_single_persona, persona_name, persona_msg, state['section_summary']): persona_name
            for persona_name, persona_msg in personas
        }
        for future in concurrent.futures.as_completed(future_to_persona):
            persona_name, output = future.result()
            state['persona_outputs'][persona_name] = output
            logger.debug(f"Completed persona: {persona_name}")
    
    return state

def process_single_persona(persona_name: str, persona_msg: str, section_summary: str) -> Tuple[str, str]:
    """
    Process a single persona analysis.
    
    Args:
        persona_name: Name of the persona
        persona_msg: System message for the persona
        section_summary: Current section summary
        
    Returns:
        Tuple of (persona_name, analysis)
    """
    agent = GeminiAgent(
        name=f"{persona_name}_agent",
        system_message=persona_msg
    )
    return persona_name, agent.generate_reply([{'role': 'user', 'content': section_summary}])

def validate_output(state: AgentState) -> AgentState:
    """
    Validate the current outputs and provide feedback.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with validation results
    """
    logger.info(f"Validation attempt {state['current_attempt'] + 1}")
    validation_agent = GeminiAgent(
        name="validation_agent",
        system_message="""You are a validation agent. Cross-check the following summaries and insights against the provided statistics. 
        Flag any hallucinations or unsupported claims. If you find issues, specify which parts need to be rerun by including either 'QUESTION' or 'SECTION' in your response.
        If all is well, include the word 'APPROVED' in your response. Be specific about what needs to be fixed and why."""
    )
    
    validation_prompt = f"Summaries:\n{json.dumps({'per_question': state['per_question_outputs'], 'section_summary': state['section_summary'], 'personas': state['persona_outputs']}, indent=2)}\n\nStatistics:\n{json.dumps(get_section4_stats(), indent=2)}"
    state['validation'] = validation_agent.generate_reply([{'role': 'user', 'content': validation_prompt}])
    
    # Extract feedback and update rerun flags
    state['validation_feedback'] = state['validation']
    state['needs_question_rerun'] = "QUESTION" in state['validation'].upper()
    state['needs_section_rerun'] = "SECTION" in state['validation'].upper()
    
    return state

def should_continue(state: AgentState) -> str:
    """
    Determine the next step in the workflow based on validation results.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node identifier
    """
    if "APPROVED" in state['validation'].upper():
        return "end"
    if state['current_attempt'] >= 2:  # max 3 attempts (0-based)
        return "end"
    if state['needs_question_rerun']:
        return "questions"
    if state['needs_section_rerun']:
        return "section"
    return "end"

def increment_attempt(state: AgentState) -> AgentState:
    """
    Increment the retry attempt counter.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with incremented attempt counter
    """
    state['current_attempt'] += 1
    return state

def save_final_report(state: AgentState) -> AgentState:
    """
    Save the final report to a JSON file.
    
    Args:
        state: Current workflow state
        
    Returns:
        Unchanged state
    """
    logger.info("Saving final report")
    final_report = {
        "per_question": state['per_question_outputs'],
        "section_summary": state['section_summary'],
        "personas": state['persona_outputs'],
        "validation": state['validation']
    }
    output_path = 'output/section4/section4_final_report.json'
    Path('output/section4').mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(final_report, f, indent=2)
    logger.info(f"Final report saved to {output_path}")
    return state

def main():
    """
    Main function to set up and run the workflow.
    """
    # Initialize state
    initial_state: AgentState = {
        "per_question_outputs": {},
        "section_summary": "",
        "persona_outputs": {},
        "validation": "",
        "validation_feedback": "",
        "current_attempt": 0,
        "needs_question_rerun": False,
        "needs_section_rerun": False
    }
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("questions", process_questions)
    workflow.add_node("section", process_section)
    workflow.add_node("personas", process_personas)
    workflow.add_node("validate", validate_output)
    workflow.add_node("increment", increment_attempt)
    workflow.add_node("save", save_final_report)
    
    # Add edges with conditional routing
    workflow.add_edge(START, "questions")
    workflow.add_edge("questions", "section")
    workflow.add_edge("section", "personas")
    workflow.add_edge("personas", "validate")
    workflow.add_edge("validate", "increment")
    
    # Add conditional edges from increment
    workflow.add_conditional_edges(
        "increment",
        should_continue,
        {
            "questions": "questions",
            "section": "section",
            "end": "save"
        }
    )
    
    # Add final edge
    workflow.add_edge("save", END)
    
    # Compile and run graph
    app = workflow.compile()
    result = app.invoke(initial_state)
    
    return result

if __name__ == "__main__":
    main()
