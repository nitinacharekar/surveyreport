"""
Summary Agent using LangGraph

This module implements a multi-agent system for analyzing and summarizing statistical data.
It uses a graph-based workflow to coordinate multiple agents that process questions,
create summaries, and validate outputs with retry capabilities.

The workflow consists of:
1. Question processing for each section
2. Section summarization for each section
3. Combined section analysis
4. Country based analysis
5. Persona analysis (parallel)
6. Validation with feedback loop
"""

import os
import json
from pathlib import Path
from statistical_analysis.Section1.section1_full_stats import get_section1_stats
from statistical_analysis.Section2.section2_full_stats import get_section2_stats
from statistical_analysis.Section3.section3_full_stats import get_section3_stats
from statistical_analysis.Section4.section4_full_stats import get_section4_stats
import openai
import autogen
import concurrent.futures
import re
import logging
from typing import Dict, List, Tuple, Any, Optional, TypedDict
from dataclasses import dataclass
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
openai.api_key = OPENAI_API_KEY

# Add this constant near the top
MAX_RETRIES = 0  # Set to 0 for now, increase to allow retries

def openai_llm(prompt: str) -> str:
    """
    Generate a response using OpenAI's GPT-4.
    
    Args:
        prompt: The input prompt for the LLM
        
    Returns:
        The generated text response
    """
    logger.info(f"Generating response for prompt of length {len(prompt)}")
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant that analyzes and summarizes data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    logger.debug(f"Generated response: {response.choices[0].message.content[:100]}...")
    return response.choices[0].message.content

class OpenAIAgent(autogen.ConversableAgent):
    """
    Custom agent implementation using OpenAI GPT-4.
    Extends the base ConversableAgent with OpenAI-specific functionality.
    """
    
    def __init__(self, name: str, system_message: str):
        """
        Initialize the OpenAI agent.
        
        Args:
            name: Unique identifier for the agent
            system_message: The system message defining the agent's role and behavior
        """
        super().__init__(name=name, llm_config=None, system_message=system_message)
        logger.info(f"Initialized OpenAIAgent: {name}")
    
    def generate_reply(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a reply using OpenAI GPT-4.
        
        Args:
            messages: List of message dictionaries containing the conversation history
            
        Returns:
            The generated reply text
        """
        prompt = messages[-1]['content']
        logger.info(f"Agent {self.name} generating reply")
        return openai_llm(prompt)

# State Management
class AgentState(TypedDict):
    """
    Type definition for the agent state.
    Tracks all necessary information throughout the workflow.
    """
    section1_outputs: Dict[str, str]  # Section 1 question analyses
    section2_outputs: Dict[str, str]  # Section 2 question analyses
    section3_outputs: Dict[str, str]  # Section 3 question analyses
    section4_outputs: Dict[str, str]  # Section 4 question analyses
    section1_summary: str             # Section 1 summary
    section2_summary: str             # Section 2 summary
    section3_summary: str             # Section 3 summary
    section4_summary: str             # Section 4 summary
    combined_summary: str             # Combined analysis of all sections
    country_analysis: Dict[str, str]  # Country-specific analyses
    country_summary: str              # Combined country analysis summary
    persona_outputs: Dict[str, str]   # Persona-specific interpretations
    validation: str                   # Current validation result
    validation_feedback: str          # Detailed feedback for improvements
    current_attempt: int             # Current retry attempt number
    needs_section_rerun: Dict[str, bool]  # Flags for section rerun
    phase: str                       # Current workflow phase
    current_section: str             # Current section being processed
    validation_passed: str           # Validation passed flag
    retry_counts: Dict[str, int]     # Retry counts per phase

# Node Functions
def process_single_question(section: str, q: str, stats: Dict[str, Any], state: AgentState) -> Tuple[str, str]:
    """
    Process a single question with its statistics.
    
    Args:
        section: Section identifier
        q: Question identifier
        stats: Statistics for the question
        state: Current workflow state
        
    Returns:
        Tuple of (question_id, analysis)
    """
    feedback_prompt = ""
    if state['validation_feedback'] and state['needs_section_rerun'].get(section, False):
        feedback_prompt = f"\n\nPrevious validation feedback: {state['validation_feedback']}\nPlease address these issues in your analysis."
    
    agent = OpenAIAgent(
        name=f"{section}_{q}_agent",
        system_message=f"""You are an expert analyst for {section} - {q}. Provide a brief, reasoned analysis based on the data below. Only cite specific data points as evidence to support your claims. Do not simply restate the data. Focus on drawing insights, trends, or implications, and use the data only to support your reasoning. Be extremely concise (1-2 sentences).{feedback_prompt}"""
    )
    prompt = f"Statistics:\n{json.dumps(stats, indent=2)}"
    return q, agent.generate_reply([{'role': 'user', 'content': prompt}])

def process_section_questions(section: str, state: AgentState) -> AgentState:
    """
    Process all questions for a specific section in parallel.
    
    Args:
        section: Section identifier
        state: Current workflow state
        
    Returns:
        Updated state with section question analyses
    """
    logger.info(f"Processing questions for {section} in parallel")
    
    # Get section stats
    section_stats = {
        'section1': get_section1_stats,
        'section2': get_section2_stats,
        'section3': get_section3_stats,
        'section4': get_section4_stats
    }[section]()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_question = {
            executor.submit(process_single_question, section, q, stats, state): q 
            for q, stats in section_stats.items()
        }
        for future in concurrent.futures.as_completed(future_to_question):
            q, output = future.result()
            state[f'{section}_outputs'][q] = output
            logger.debug(f"Completed {section} question: {q}")
    
    return state

def process_section_summary(section: str, state: AgentState) -> AgentState:
    """
    Process the section summary based on question analyses.
    
    Args:
        section: Section identifier
        state: Current workflow state
        
    Returns:
        Updated state with section summary
    """
    logger.info(f"Processing {section} summary")
    feedback_prompt = ""
    if state['validation_feedback'] and state['needs_section_rerun'].get(section, False):
        feedback_prompt = f"\n\nPrevious validation feedback: {state['validation_feedback']}\nPlease address these issues in your synthesis."
    
    section_moderator = OpenAIAgent(
        name=f"{section}_moderator",
        system_message=f"""You are a Section Moderator for {section}. Synthesize the following per-question summaries into exactly 4 sentences maximum. Focus on the most important cross-question patterns and key findings. Provide a reasoned analysis, using data only as evidence to support your claims. Do not simply restate or regurgitate the data. Draw insights, trends, or implications, and use the data only to support your reasoning. Be extremely concise and avoid any redundancy.{feedback_prompt}"""
    )
    section_prompt = "\n\n".join(state[f'{section}_outputs'].values())
    state[f'{section}_summary'] = section_moderator.generate_reply([{'role': 'user', 'content': section_prompt}])
    return state

def process_combined_summary(state: AgentState) -> AgentState:
    """
    Process the combined summary of all sections.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with combined summary
    """
    logger.info("Processing combined summary")
    feedback_prompt = ""
    if state['validation_feedback']:
        feedback_prompt = f"\n\nPrevious validation feedback: {state['validation_feedback']}\nPlease address these issues in your synthesis."
    
    combined_moderator = OpenAIAgent(
        name="combined_moderator",
        system_message=f"""You are a combined analysis moderator. Analyze the following section summaries of responses to an API Security survey and provide an overall summary of global API Security trends, strengths, weaknesses, and unique characteristics. Don't focus on outputting the data, focus on the analysis and overall summary. 
        {feedback_prompt}"""
    )
    
    section_summaries = {
        'Section 1': state['section1_summary'],
        'Section 2': state['section2_summary'],
        'Section 3': state['section3_summary'],
        'Section 4': state['section4_summary']
    }
    
    combined_prompt = "\n\n".join([f"{section}:\n{summary}" for section, summary in section_summaries.items()])
    state['combined_summary'] = combined_moderator.generate_reply([{'role': 'user', 'content': combined_prompt}])
    return state

def process_country_analysis(state: AgentState) -> AgentState:
    """
    Aggregate demographic data by country from all section stats and generate OpenAI insights.
    """
    logger.info("Processing country analysis node...")

    # Load all section stats
    all_section_stats = {
        'Section1': get_section1_stats(),
        'Section2': get_section2_stats(),
        'Section3': get_section3_stats(),
        'Section4': get_section4_stats(),
    }

    # Aggregate by country using improved logic
    country_data = {}
    for section, section_stats in all_section_stats.items():
        for qkey, summary in section_stats.items():
            demo_summary = summary.get('demographic_analysis')
            if not demo_summary:
                continue
            total_responses_by_demo = demo_summary.get('total_responses_by_demo', {})
            for demo_col, country_counts in total_responses_by_demo.items():
                for country, count in country_counts.items():
                    if country not in country_data:
                        country_data[country] = {}
                    country_data[country][f'{section}_{qkey}'] = {
                        'total_responses': count,
                        'question_text': demo_summary.get('question_text'),
                        # Add more fields if needed from demo_summary['statistics']
                    }
    logger.info(f"Countries found: {list(country_data.keys())}")

    # Generate insights for each country using OpenAI
    insights = {}
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    for country, summary in country_data.items():
        logger.info(f"Generating insight for {country}...")
        prompt = f"""
You are an expert in API Security analysis. Based on the following demographic and statistical data for {country}, provide a detailed, data-driven analysis of API Security trends, strengths, weaknesses, and unique characteristics for this country. 

- Highlight what makes this country stand out compared to other countries.
- Identify any outliers, surprising results, or unique patterns in the data.
- Use specific data points as evidence for your claims (percentages, counts, averages, etc.).
- Avoid generic statements; focus on what is truly unique or notable for this country.
- Avoid talking about counts of people who participated in total for a question, instead focus on the specific answers to the questions.
- Do not use information that does not exist in the data.

Demographic and Statistical Data:
{json.dumps(summary, indent=2)}
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert API Security analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        insights[country] = response.choices[0].message.content.strip()
        logger.info(f"Insight for {country}: {insights[country]}")

    # Store in state
    state['country_analysis'] = insights
    return state

def process_personas(state: AgentState) -> AgentState:
    """
    Process persona analyses in parallel, using both the combined summary and country demographic data.
    """
    logger.info("Processing personas in parallel")
    personas = [
        ("Customer", "You are a customer. Interpret these section insights from your perspective. What stands out? What actions or concerns would you have?"),
        ("Business Customer", "You are a business customer. Interpret these section insights from your perspective. What stands out? What actions or concerns would you have?"),
        ("F5 Vendor", "You are F5 Networks, the vendor. Interpret these section insights from your perspective. What stands out? What actions or concerns would you have?")
    ]
    country_data = state.get('country_analysis', {})
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_persona = {
            executor.submit(process_single_persona, persona_name, persona_msg, state['combined_summary'], country_data): persona_name
            for persona_name, persona_msg in personas
        }
        for future in concurrent.futures.as_completed(future_to_persona):
            persona_name, output = future.result()
            state['persona_outputs'][persona_name] = output
            logger.debug(f"Completed persona: {persona_name}")
    return state

def process_single_persona(persona_name: str, persona_msg: str, combined_summary: str, country_data: dict) -> Tuple[str, str]:
    """
    Process a single persona analysis, including demographic/country data in the prompt.
    """
    prompt = (
        f"{combined_summary}\n\n"
        f"Here is detailed demographic and country-specific data:\n"
        f"{json.dumps(country_data, indent=2)}"
    )
    agent = OpenAIAgent(
        name=f"{persona_name}_agent",
        system_message=f"{persona_msg} Provide your interpretation in exactly 2 sentences maximum. Focus on reasoning and analysis, using data only as evidence to support your claims. Do not simply restate or regurgitate the data. Be extremely concise."
    )
    return persona_name, agent.generate_reply([{'role': 'user', 'content': prompt}])

def validate_output(state: AgentState) -> AgentState:
    """
    Central validation node: validates outputs for different workflow phases based on 'phase' in state.
    Args:
        state: Current workflow state, must include 'phase' key (e.g., 'section', 'combined', 'country', 'persona')
    Returns:
        Updated state with validation results
    """
    phase = state.get('phase', 'generic')
    logger.info(f"Validation attempt {state['current_attempt'] + 1} for phase: {phase}")

    # Select output and prompt based on phase
    if phase == 'section':
        section = state.get('current_section', 'section1')
        output = state.get(f'{section}_summary', '')
        prompt = f"Validate the following summary for {section}. Check for accuracy, clarity, and data support. Flag any hallucinations or unsupported claims.\n\nSummary:\n{output}"
    elif phase == 'combined':
        output = state.get('combined_summary', '')
        prompt = f"Validate the following combined summary of all sections. Check for accuracy, clarity, and data support. Flag any hallucinations or unsupported claims.\n\nCombined Summary:\n{output}"
    elif phase == 'country':
        output = state.get('country_analysis', {})
        prompt = f"Validate the following country analysis. Check for accuracy, clarity, and data support. Flag any hallucinations or unsupported claims.\n\nCountry Analysis:\n{json.dumps(output, indent=2)}"
    elif phase == 'persona':
        output = state.get('persona_outputs', {})
        prompt = f"Validate the following persona interpretations. Check for accuracy, clarity, and data support. Flag any hallucinations or unsupported claims.\n\nPersona Outputs:\n{json.dumps(output, indent=2)}"
    else:
        output = state.get('combined_summary', '')
        prompt = f"Validate the following output. Check for accuracy, clarity, and data support. Flag any hallucinations or unsupported claims.\n\nOutput:\n{output}"

    validation_agent = OpenAIAgent(
        name="validation_agent",
        system_message="You are a validation agent. Cross-check the following output against the provided statistics. Flag any hallucinations or unsupported claims in exactly 2 sentences maximum. Focus on reasoning and analysis, using data only as evidence to support your claims. If you find issues, specify which sections need to be rerun. Return APPROVED if all is well. Only respond with one sentence."
    )

    state['validation'] = validation_agent.generate_reply([{'role': 'user', 'content': prompt}])
    state['validation_feedback'] = state['validation']
    # Set validation_passed flag
    state['validation_passed'] = "APPROVED" in state['validation'].upper()
    # Track retry counts per phase
    if 'retry_counts' not in state:
        state['retry_counts'] = {}
    if not state['validation_passed']:
        state['retry_counts'][phase] = state['retry_counts'].get(phase, 0) + 1
    # Optionally, set rerun flags based on feedback (for section phase)
    if phase == 'section':
        section = state.get('current_section', 'section1')
        state['needs_section_rerun'][section] = section.upper() in state['validation'].upper()
    return state

# Add this function for routing after validation
def validation_routing(state: AgentState) -> str:
    phase = state.get('phase', 'generic')
    retries = state.get('retry_counts', {}).get(phase, 0)
    if not state.get('validation_passed', False) and retries <= MAX_RETRIES:
        # Route back to the phase that needs to be redone
        if phase == "section":
            return f"process_{state.get('current_section', 'section1')}"
        elif phase == "combined":
            return "process_combined"
        elif phase == "country":
            return "process_country"
        elif phase == "persona":
            return "process_personas"
    # Otherwise, proceed forward
    if phase == "section":
        # Route to next section or combined, etc.
        next_section = {
            "section1": "process_section2",
            "section2": "process_section3",
            "section3": "process_section4",
            "section4": "process_combined"
        }.get(state.get('current_section', 'section1'), "process_combined")
        return next_section
    elif phase == "combined":
        return "process_country"
    elif phase == "country":
        return "process_personas"
    elif phase == "persona":
        return "increment_attempt"
    return "increment_attempt"

def should_continue(state: AgentState) -> str:
    """
    Determine the next step in the workflow based on validation results.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node identifier
    """
    # Always end after first validation attempt
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
    Save the final report to a JSON file and a text file.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state
    """
    logger.info("Saving final report")
    
    # Save JSON report
    report = {
        'section_summaries': {
            'section1': state['section1_summary'],
            'section2': state['section2_summary'],
            'section3': state['section3_summary'],
            'section4': state['section4_summary']
        },
        'combined_summary': state['combined_summary'],
        'country_analysis': state['country_analysis'],
        'country_summary': state['country_summary'],
        'persona_outputs': state['persona_outputs']
    }
    
    with open('output/final_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save text report
    with open('output/final_report3.md', 'w') as f:
        f.write("=== Final Report ===\n\n")

        f.write("--- Overall Summary ---\n")
        f.write(f"{report['combined_summary']}\n\n")
        
        f.write("--- Section Summaries ---\n")
        for section, summary in report['section_summaries'].items():
            f.write(f"{section}:\n{summary}\n\n")
    
        f.write("--- Country Analysis ---\n")
        for country, analysis in report['country_analysis'].items():
            f.write(f"{country}:\n{analysis}\n\n")
    return state

def set_phase(state: AgentState, phase: str, current_section: str = None) -> AgentState:
    state['phase'] = phase
    if current_section:
        state['current_section'] = current_section
    return state

def main():
    """
    Main function to set up and run the workflow.
    """
    # Initialize state
    initial_state: AgentState = {
        "section1_outputs": {},
        "section2_outputs": {},
        "section3_outputs": {},
        "section4_outputs": {},
        "section1_summary": "",
        "section2_summary": "",
        "section3_summary": "",
        "section4_summary": "",
        "combined_summary": "",
        "country_analysis": {},
        "country_summary": "",
        "persona_outputs": {},
        "validation": "",
        "validation_feedback": "",
        "current_attempt": 0,
        "needs_section_rerun": {
            "section1": False,
            "section2": False,
            "section3": False,
            "section4": False
        },
        "phase": "generic",
        "current_section": "section1",
        "validation_passed": "",
        "retry_counts": {}
    }
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes for each section
    for section in ['section1', 'section2', 'section3', 'section4']:
        workflow.add_node(f"process_{section}", lambda s, sec=section: process_section_questions(sec, s))
        workflow.add_node(f"summarize_{section}", lambda s, sec=section: process_section_summary(sec, s))
        workflow.add_node(f"set_phase_{section}", lambda s, sec=section: set_phase(s, "section", sec))
    
    # Add other nodes
    workflow.add_node("process_combined", process_combined_summary)
    workflow.add_node("set_phase_combined", lambda s: set_phase(s, "combined"))
    workflow.add_node("process_country", process_country_analysis)
    workflow.add_node("set_phase_country", lambda s: set_phase(s, "country"))
    workflow.add_node("process_personas", process_personas)
    workflow.add_node("set_phase_persona", lambda s: set_phase(s, "persona"))
    workflow.add_node("validate_output", validate_output)
    workflow.add_node("increment_attempt", increment_attempt)
    workflow.add_node("save_report", save_final_report)
    
    # Add edges for section 1
    workflow.add_edge(START, "process_section1")
    workflow.add_edge("process_section1", "summarize_section1")
    workflow.add_edge("summarize_section1", "set_phase_section1")
    workflow.add_edge("set_phase_section1", "validate_output")
    workflow.add_edge("validate_output", "process_section2")
    
    # Section 2
    workflow.add_edge("process_section2", "summarize_section2")
    workflow.add_edge("summarize_section2", "set_phase_section2")
    workflow.add_edge("set_phase_section2", "validate_output")
    workflow.add_edge("validate_output", "process_section3")
    
    # Section 3
    workflow.add_edge("process_section3", "summarize_section3")
    workflow.add_edge("summarize_section3", "set_phase_section3")
    workflow.add_edge("set_phase_section3", "validate_output")
    workflow.add_edge("validate_output", "process_section4")
    
    # Section 4
    workflow.add_edge("process_section4", "summarize_section4")
    workflow.add_edge("summarize_section4", "set_phase_section4")
    workflow.add_edge("set_phase_section4", "validate_output")
    workflow.add_edge("validate_output", "process_combined")
    
    # Combined summary
    workflow.add_edge("process_combined", "set_phase_combined")
    workflow.add_edge("set_phase_combined", "validate_output")
    workflow.add_edge("validate_output", "process_country")
    
    # Country analysis
    workflow.add_edge("process_country", "set_phase_country")
    workflow.add_edge("set_phase_country", "validate_output")
    workflow.add_edge("validate_output", "process_personas")
    
    # Persona analysis
    workflow.add_edge("process_personas", "set_phase_persona")
    workflow.add_edge("set_phase_persona", "validate_output")
    workflow.add_edge("validate_output", "increment_attempt")
    
    # Add conditional validation routing after each validate_output
    workflow.add_conditional_edges(
        "validate_output",
        validation_routing,
        {
            "process_section1": "process_section1",
            "process_section2": "process_section2",
            "process_section3": "process_section3",
            "process_section4": "process_section4",
            "process_combined": "process_combined",
            "process_country": "process_country",
            "process_personas": "process_personas",
            "increment_attempt": "increment_attempt"
        }
    )
    
    # Add conditional edges from increment
    workflow.add_conditional_edges(
        "increment_attempt",
        should_continue,
        {
            "end": "save_report"  # Only end option now
        }
    )
    
    # Add final edge
    workflow.add_edge("save_report", END)
    
    # Compile and run graph
    app = workflow.compile()
    result = app.invoke(initial_state)
    
    return result

if __name__ == "__main__":
    main()
