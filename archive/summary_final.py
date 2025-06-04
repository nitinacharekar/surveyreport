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
from typing_extensions import Annotated

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
    section1_outputs: Annotated[Dict[str, str], "accumulate"]  # Section 1 question analyses
    section2_outputs: Annotated[Dict[str, str], "accumulate"]  # Section 2 question analyses
    section3_outputs: Annotated[Dict[str, str], "accumulate"]  # Section 3 question analyses
    section4_outputs: Annotated[Dict[str, str], "accumulate"]  # Section 4 question analyses
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
    Process all questions for a specific section sequentially.
    """
    logger.info(f"Processing questions for {section} sequentially")
    section_stats = {
        'section1': get_section1_stats,
        'section2': get_section2_stats,
        'section3': get_section3_stats,
        'section4': get_section4_stats
    }[section]()
    outputs = {}
    for q, stats in section_stats.items():
        qid, output = process_single_question(section, q, stats, state)
        outputs[qid] = output
    state[f'{section}_outputs'] = outputs
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
        system_message=f"""You are a Combined Analysis Moderator. Synthesize the following section summaries into exactly 4 sentences maximum. Focus only on the most significant cross-section patterns and key insights. Provide a reasoned analysis, using data only as evidence to support your claims. Do not simply restate or regurgitate the data. Draw insights, trends, or implications, and use the data only to support your reasoning. Be extremely concise and avoid any redundancy.{feedback_prompt}"""
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
You are an expert in API Security analysis. Based on the following demographic data for {country}, generate a concise insight (2-3 sentences) about API Security trends, strengths, or weaknesses for this country. Use the data to highlight any notable patterns or differences and include precise data points for evidence.

Demographic Data:
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
    Validate the current outputs and provide feedback.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with validation results
    """
    logger.info(f"Validation attempt {state['current_attempt'] + 1}")
    validation_agent = OpenAIAgent(
        name="validation_agent",
        system_message="""You are a validation agent. Cross-check the following summaries and insights against the provided statistics. Flag any hallucinations or unsupported claims in exactly 2 sentences maximum. Focus on reasoning and analysis, using data only as evidence to support your claims. Do not simply restate or regurgitate the data. If you find issues, specify which sections need to be rerun. If all is well, include the word 'APPROVED' in your response. Be extremely concise."""
    )
    
    all_stats = {
        'section1': get_section1_stats(),
        'section2': get_section2_stats(),
        'section3': get_section3_stats(),
        'section4': get_section4_stats()
    }
    
    validation_prompt = f"Summaries:\n{json.dumps({
        'section_summaries': {f'section{i}': state[f'section{i}_summary'] for i in range(1, 5)},
        'combined_summary': state['combined_summary'],
        #'country_analysis': state['country_analysis'],
        'country_summary': state['country_summary'],
        'personas': state['persona_outputs']
    }, indent=2)}\n\nStatistics:\n{json.dumps(all_stats, indent=2)}"
    
    state['validation'] = validation_agent.generate_reply([{'role': 'user', 'content': validation_prompt}])
    
    # Extract feedback and update rerun flags
    state['validation_feedback'] = state['validation']
    for section in ['section1', 'section2', 'section3', 'section4']:
        state['needs_section_rerun'][section] = section.upper() in state['validation'].upper()
    
    return state

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
    with open('output/final_report.txt', 'w') as f:
        f.write("=== Final Report ===\n\n")
        
        f.write("--- Section Summaries ---\n")
        for section, summary in report['section_summaries'].items():
            f.write(f"{section}:\n{summary}\n\n")
        
        f.write("--- Combined Summary ---\n")
        f.write(f"{report['combined_summary']}\n\n")
        
        f.write("--- Country Analysis ---\n")
        for country, analysis in report['country_analysis'].items():
            f.write(f"{country}:\n{analysis}\n\n")
        
        f.write("--- Country Summary ---\n")
        f.write(f"{report['country_summary']}\n\n")
    
    return state

def join_summaries(state: AgentState) -> AgentState:
    # Synchronization point; all section summaries should be in state
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
        }
    }
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes for each section
    for section in ['section1', 'section2', 'section3', 'section4']:
        workflow.add_node(f"process_{section}", lambda s, sec=section: process_section_questions(sec, s))
        workflow.add_node(f"summarize_{section}", lambda s, sec=section: process_section_summary(sec, s))
    
    # Add parallel edges from START to each section processor
    workflow.add_edge(START, "process_section1")
    workflow.add_edge(START, "process_section2")
    workflow.add_edge(START, "process_section3")
    workflow.add_edge(START, "process_section4")
    
    # Chain each section's processing to its summarization
    for section in ['section1', 'section2', 'section3', 'section4']:
        workflow.add_edge(f"process_{section}", f"summarize_{section}")
    
    # Add a join node that waits for all summarize_sectionX nodes
    workflow.add_node("join_summaries", join_summaries)
    for section in ['section1', 'section2', 'section3', 'section4']:
        workflow.add_edge(f"summarize_{section}", "join_summaries")
    
    # After join, continue as before
    workflow.add_node("process_combined", process_combined_summary)
    workflow.add_node("process_country", process_country_analysis)
    workflow.add_node("process_personas", process_personas)
    workflow.add_node("validate_output", validate_output)
    workflow.add_node("increment_attempt", increment_attempt)
    workflow.add_node("save_report", save_final_report)
    
    workflow.add_edge("join_summaries", "process_combined")
    workflow.add_edge("process_combined", "process_country")
    workflow.add_edge("process_country", "process_personas")
    workflow.add_edge("process_personas", "validate_output")
    workflow.add_edge("validate_output", "increment_attempt")
    workflow.add_conditional_edges(
        "increment_attempt",
        should_continue,
        {
            "end": "save_report"  # Only end option now
        }
    )
    workflow.add_edge("save_report", END)
    
    # Compile and run graph
    app = workflow.compile()
    result = app.invoke(initial_state)
    
    return result

if __name__ == "__main__":
    main()
