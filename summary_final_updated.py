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
from langchain_core.runnables.config import RunnableConfig

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
    section1_outputs: Dict[str, str]
    section2_outputs: Dict[str, str]
    section3_outputs: Dict[str, str]
    section4_outputs: Dict[str, str]
    section1_summary: str
    section2_summary: str
    section3_summary: str
    section4_summary: str
    combined_summary: str
    country_analysis: Dict[str, str]
    country_summary: str
    persona_outputs: Dict[str, str]
    validation: str
    validation_feedback: str
    section_attempts: Dict[str, int]  # Track attempts per section
    max_attempts: int  # Maximum number of retry attempts
    needs_section_rerun: Dict[str, bool]

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

def increment_attempt(state: AgentState, section: str) -> AgentState:
    """
    Increment the retry attempt counter for a specific section and log the attempt.
    """
    # Only increment the attempt counter for a section if a rerun is actually needed
    if 'section_attempts' not in state:
        state['section_attempts'] = {}
    if section not in state['section_attempts']:
        state['section_attempts'][section] = 0
    old_attempt = state['section_attempts'][section]
    if state['needs_section_rerun'].get(section, False):
        state['section_attempts'][section] += 1
        logger.info(f"Incrementing attempt counter for {section} from {old_attempt} to {state['section_attempts'][section]} (max: {state['max_attempts']})")
    else:
        logger.info(f"Not incrementing attempt counter for {section} because needs_section_rerun is False.")
    logger.info(f"Current rerun flags: {json.dumps(state['needs_section_rerun'], indent=2)}")
    return state

def should_rerun_section(section: str, state: AgentState) -> bool:
    """
    Determine if a section needs to be rerun based on validation state and attempt count.
    """
    current_attempt = state['section_attempts'].get(section, 0)
    if current_attempt >= state['max_attempts']:
        logger.info(f"Max attempts ({state['max_attempts']}) reached for {section}, skipping rerun")
        return False
    logger.info(f"Checking rerun for {section}: attempt {current_attempt}/{state['max_attempts']}, needs_rerun={state['needs_section_rerun'].get(section, False)}")
    return state['needs_section_rerun'].get(section, False)

def validate_section_output(state: AgentState, section: str) -> AgentState:
    """
    Validate section outputs and summary together.
    """
    # Log the validation attempt for this section
    logger.info(f"Validating {section} outputs and summary (Attempt {state['section_attempts'].get(section, 0)}/{state['max_attempts']})")
    outputs = state.get(f'{section}_outputs', {})
    summary = state.get(f'{section}_summary', '')
    # Create a validation agent with strict instructions and examples for output format
    validation_agent = OpenAIAgent(
        name=f"{section}_validation_agent",
        system_message=f"""You are a validation agent for {section}. Review the section outputs and summary for accuracy, consistency, and data support.\nIf everything is valid, respond with exactly APPROVED.\nIf not, respond with exactly REJECTED: <reason>.\nDo not provide any other text or explanation.\nFor example:\n- APPROVED\n- REJECTED: The summary does not match the outputs.\nIf you do not follow this format, your response will be discarded."""
    )
    # Add a user prompt reminder to reinforce the required format
    prompt = f"Remember: Only respond with 'APPROVED' or 'REJECTED: <reason>'. Do not provide any other text.\n\nValidate the following {section} outputs and summary:\n\nOutputs:\n{json.dumps(outputs, indent=2)}\n\nSummary:\n{summary}"
    # Get the validation agent's reply
    state['validation'] = validation_agent.generate_reply([{'role': 'user', 'content': prompt}])
    state['validation_feedback'] = state['validation']
    # Only treat as passed if the response starts with 'APPROVED'
    state['validation_passed'] = state['validation'].strip().upper().startswith("APPROVED")
    if not state['validation_passed']:
        # If validation failed, set rerun flag if under max attempts
        current_attempt = state['section_attempts'].get(section, 0)
        if current_attempt < state['max_attempts']:
            state['needs_section_rerun'][section] = True
            logger.info(f"Validation failed for {section} - will retry (Attempt {current_attempt + 1}/{state['max_attempts']})")
        else:
            logger.info(f"Validation failed for {section} but max attempts reached")
        logger.info(f"Validation feedback: {state['validation_feedback']}")
    else:
        # Reset rerun flag if validation passed
        if state['needs_section_rerun'].get(section, False):
            logger.info(f"Resetting needs_section_rerun[{section}] to False after successful validation.")
        state['needs_section_rerun'][section] = False
        logger.info(f"Validation passed for {section} (Attempt {state['section_attempts'].get(section, 0)}/{state['max_attempts']})")
    return state

def validate_combined_output(state: AgentState) -> AgentState:
    """
    Validate combined summary against all section summaries.
    """
    # Log the validation attempt for the combined summary
    logger.info(f"Validating combined summary (Attempt {state['section_attempts'].get('combined', 0)}/{state['max_attempts']})")
    combined_summary = state.get('combined_summary', '')
    section_summaries = {
        'section1': state.get('section1_summary', ''),
        'section2': state.get('section2_summary', ''),
        'section3': state.get('section3_summary', ''),
        'section4': state.get('section4_summary', '')
    }
    # Create a validation agent with strict instructions and examples for output format
    validation_agent = OpenAIAgent(
        name="combined_validation_agent",
        system_message="""You are a validation agent for the combined summary. Review the combined summary against all section summaries for accuracy, consistency, and data support.\nIf everything is valid, respond with exactly APPROVED.\nIf not, respond with exactly REJECTED: <reason>.\nDo not provide any other text or explanation.\nFor example:\n- APPROVED\n- REJECTED: The summary does not match the outputs.\nIf you do not follow this format, your response will be discarded."""
    )
    # Add a user prompt reminder to reinforce the required format
    prompt = f"Remember: Only respond with 'APPROVED' or 'REJECTED: <reason>'. Do not provide any other text.\n\nValidate the following combined summary against section summaries:\n\nCombined Summary:\n{combined_summary}\n\nSection Summaries:\n{json.dumps(section_summaries, indent=2)}"
    # Get the validation agent's reply
    state['validation'] = validation_agent.generate_reply([{'role': 'user', 'content': prompt}])
    state['validation_feedback'] = state['validation']
    # Only treat as passed if the response starts with 'APPROVED'
    state['validation_passed'] = state['validation'].strip().upper().startswith("APPROVED")
    if not state['validation_passed']:
        # If validation failed, set rerun flag if under max attempts
        current_attempt = state['section_attempts'].get('combined', 0)
        if current_attempt < state['max_attempts']:
            state['needs_section_rerun']['combined'] = True
            logger.info(f"Validation failed for combined summary - will retry (Attempt {current_attempt + 1}/{state['max_attempts']})")
        else:
            logger.info("Validation failed for combined summary but max attempts reached")
        logger.info(f"Validation feedback: {state['validation_feedback']}")
    else:
        # Reset rerun flag if validation passed
        if state['needs_section_rerun'].get('combined', False):
            logger.info(f"Resetting needs_section_rerun['combined'] to False after successful validation.")
        state['needs_section_rerun']['combined'] = False
        logger.info(f"Validation passed for combined summary (Attempt {state['section_attempts'].get('combined', 0)}/{state['max_attempts']})")
    return state

def validate_country_output(state: AgentState) -> AgentState:
    """
    Validate all country analyses at once and determine if the entire country analysis needs to be rerun.
    """
    # Log the validation attempt for country analyses
    logger.info(f"Validating all country analyses (Attempt {state['section_attempts'].get('country', 0)}/{state['max_attempts']})")
    country_analyses = state.get('country_analysis', {})
    # Create a validation agent with strict instructions and examples for output format
    validation_agent = OpenAIAgent(
        name="country_validation_agent",
        system_message="""You are a validation agent for country analyses. Review all country analyses for accuracy, consistency, and data support.\nIf everything is valid, respond with exactly APPROVED.\nIf not, respond with exactly REJECTED: <reason>.\nDo not provide any other text or explanation.\nFor example:\n- APPROVED\n- REJECTED: The summary does not match the outputs.\nIf you do not follow this format, your response will be discarded."""
    )
    # Add a user prompt reminder to reinforce the required format
    prompt = f"Remember: Only respond with 'APPROVED' or 'REJECTED: <reason>'. Do not provide any other text.\n\nValidate the following country analyses:\n\n{json.dumps(country_analyses, indent=2)}"
    # Get the validation agent's reply
    state['validation'] = validation_agent.generate_reply([{'role': 'user', 'content': prompt}])
    state['validation_feedback'] = state['validation']
    # Only treat as passed if the response starts with 'APPROVED'
    state['validation_passed'] = state['validation'].strip().upper().startswith("APPROVED")
    if not state['validation_passed']:
        # If validation failed, set rerun flag if under max attempts
        current_attempt = state['section_attempts'].get('country', 0)
        if current_attempt < state['max_attempts']:
            state['needs_section_rerun']['country'] = True
            logger.info(f"Validation failed for country analyses - will retry (Attempt {current_attempt + 1}/{state['max_attempts']})")
        else:
            logger.info("Validation failed for country analyses but max attempts reached")
        logger.info(f"Validation feedback: {state['validation_feedback']}")
    else:
        # Reset rerun flag if validation passed
        if state['needs_section_rerun'].get('country', False):
            logger.info(f"Resetting needs_section_rerun['country'] to False after successful validation.")
        state['needs_section_rerun']['country'] = False
        logger.info(f"Validation passed for country analyses (Attempt {state['section_attempts'].get('country', 0)}/{state['max_attempts']})")
    return state

def validate_persona_output(state: AgentState) -> AgentState:
    """
    Validate all persona outputs against combined summary and country analysis.
    """
    # Log the validation attempt for persona outputs
    logger.info(f"Validating persona outputs (Attempt {state['section_attempts'].get('personas', 0)}/{state['max_attempts']})")
    persona_outputs = state.get('persona_outputs', {})
    combined_summary = state.get('combined_summary', '')
    country_analysis = state.get('country_analysis', {})
    # Create a validation agent with strict instructions and examples for output format
    validation_agent = OpenAIAgent(
        name="persona_validation_agent",
        system_message="""You are a validation agent for persona analyses. Review all persona outputs against the combined summary and country analysis for accuracy, consistency, and data support.\nIf everything is valid, respond with exactly APPROVED.\nIf not, respond with exactly REJECTED: <reason>.\nDo not provide any other text or explanation.\nFor example:\n- APPROVED\n- REJECTED: The summary does not match the outputs.\nIf you do not follow this format, your response will be discarded."""
    )
    # Add a user prompt reminder to reinforce the required format
    prompt = f"Remember: Only respond with 'APPROVED' or 'REJECTED: <reason>'. Do not provide any other text.\n\nValidate the following persona outputs against source data:\n\nPersona Outputs:\n{json.dumps(persona_outputs, indent=2)}\n\nCombined Summary:\n{combined_summary}\n\nCountry Analysis:\n{json.dumps(country_analysis, indent=2)}"
    # Get the validation agent's reply
    state['validation'] = validation_agent.generate_reply([{'role': 'user', 'content': prompt}])
    state['validation_feedback'] = state['validation']
    # Only treat as passed if the response starts with 'APPROVED'
    state['validation_passed'] = state['validation'].strip().upper().startswith("APPROVED")
    if not state['validation_passed']:
        # If validation failed, set rerun flag if under max attempts
        current_attempt = state['section_attempts'].get('personas', 0)
        if current_attempt < state['max_attempts']:
            state['needs_section_rerun']['personas'] = True
            logger.info(f"Validation failed for personas - will retry (Attempt {current_attempt + 1}/{state['max_attempts']})")
        else:
            # If we've maxed out persona retries, check if we need to retry earlier sections
            feedback = state['validation'].lower()
            if any(section in feedback for section in ['section1', 'section2', 'section3', 'section4']):
                section_to_rerun = next(section for section in ['section1', 'section2', 'section3', 'section4'] if section in feedback)
                if state['section_attempts'].get(section_to_rerun, 0) < state['max_attempts']:
                    state['needs_section_rerun'][section_to_rerun] = True
                    logger.info(f"Validation failed for personas - will retry {section_to_rerun} (Attempt {state['section_attempts'][section_to_rerun]}/{state['max_attempts']})")
            elif 'combined' in feedback and state['section_attempts'].get('combined', 0) < state['max_attempts']:
                state['needs_section_rerun']['combined'] = True
                logger.info(f"Validation failed for personas - will retry combined (Attempt {state['section_attempts']['combined']}/{state['max_attempts']})")
            elif 'country' in feedback and state['section_attempts'].get('country', 0) < state['max_attempts']:
                state['needs_section_rerun']['country'] = True
                logger.info(f"Validation failed for personas - will retry country (Attempt {state['section_attempts']['country']}/{state['max_attempts']})")
            else:
                logger.info("Validation failed for personas but max attempts reached for all sections")
        logger.info(f"Validation feedback: {state['validation_feedback']}")
        logger.info(f"Rerun flags set: {json.dumps(state['needs_section_rerun'], indent=2)}")
    else:
        # Reset rerun flag if validation passed
        if state['needs_section_rerun'].get('personas', False):
            logger.info(f"Resetting needs_section_rerun['personas'] to False after successful validation.")
        state['needs_section_rerun']['personas'] = False
        logger.info(f"Validation passed for personas (Attempt {state['section_attempts'].get('personas', 0)}/{state['max_attempts']})")
    return state

def get_next_node(current_section: str, state: AgentState) -> str:
    """
    Determine the next node based on current section and validation state.
    """
    if current_section == 'section1':
        return 'process_section2'
    elif current_section == 'section2':
        return 'process_section3'
    elif current_section == 'section3':
        return 'process_section4'
    elif current_section == 'section4':
        return 'process_combined'
    elif current_section == 'combined':
        return 'process_country'
    elif current_section == 'country':
        return 'process_personas'
    elif current_section == 'personas':
        return 'save_report'
    return 'save_report'

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
        'persona_outputs': state['persona_outputs'],
        'retry_info': {
            'section_attempts': state['section_attempts'],
            'needs_section_rerun': state['needs_section_rerun']
        }
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
        "section_attempts": {
            "section1": 0,
            "section2": 0,
            "section3": 0,
            "section4": 0,
            "combined": 0,
            "country": 0,
            "personas": 0
        },
        "max_attempts": 1,
        "needs_section_rerun": {
            "section1": False,
            "section2": False,
            "section3": False,
            "section4": False,
            "combined": False,
            "country": False,
            "personas": False
        }
    }
    
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes for each section
    for section in ['section1', 'section2', 'section3', 'section4']:
        workflow.add_node(f"process_{section}", lambda s, sec=section: process_section_questions(sec, s))
        workflow.add_node(f"summarize_{section}", lambda s, sec=section: process_section_summary(sec, s))
        workflow.add_node(f"validate_{section}", lambda s, sec=section: validate_section_output(s, sec))
        workflow.add_node(f"increment_attempt_{section}", lambda s, sec=section: increment_attempt(s, sec))
    
    # Add other nodes
    workflow.add_node("process_combined", process_combined_summary)
    workflow.add_node("validate_combined", validate_combined_output)
    workflow.add_node("increment_attempt_combined", lambda s: increment_attempt(s, "combined"))
    workflow.add_node("process_country", process_country_analysis)
    workflow.add_node("validate_country", validate_country_output)
    workflow.add_node("increment_attempt_country", lambda s: increment_attempt(s, "country"))
    workflow.add_node("process_personas", process_personas)
    workflow.add_node("validate_personas", validate_persona_output)
    workflow.add_node("increment_attempt_personas", lambda s: increment_attempt(s, "personas"))
    workflow.add_node("save_report", save_final_report)
    
    # Add edges from START to first section
    workflow.add_edge(START, "process_section1")
    
    # Define section flow
    sections = ['section1', 'section2', 'section3', 'section4']
    for i, section in enumerate(sections):
        # Process -> Summarize -> Validate flow
        workflow.add_edge(f"process_{section}", f"summarize_{section}")
        workflow.add_edge(f"summarize_{section}", f"validate_{section}")
        
        # Get next node
        next_node = "process_combined" if i == len(sections) - 1 else f"process_{sections[i + 1]}"
        
        # Add validation edges - only go to increment_attempt if validation failed and retry is needed
        workflow.add_conditional_edges(
            f"validate_{section}",
            lambda state, s=section, n=next_node: f"increment_attempt_{s}" if not state['validation_passed'] and state['needs_section_rerun'][s] else n,
            {
                f"increment_attempt_{section}": f"increment_attempt_{section}",
                next_node: next_node
            }
        )
        
        # Add increment_attempt edges - only retry if we haven't hit max attempts
        workflow.add_conditional_edges(
            f"increment_attempt_{section}",
            lambda state, s=section, n=next_node: f"process_{s}" if state['needs_section_rerun'][s] and state['section_attempts'].get(s, 0) < state['max_attempts'] else n,
            {
                f"process_{section}": f"process_{section}",
                next_node: next_node
            }
        )
    
    # Add combined analysis flow
    workflow.add_edge("process_combined", "validate_combined")
    workflow.add_conditional_edges(
        "validate_combined",
        lambda state: "increment_attempt_combined" if not state['validation_passed'] and state['needs_section_rerun']['combined'] else "process_country",
        {
            "increment_attempt_combined": "increment_attempt_combined",
            "process_country": "process_country"
        }
    )
    
    workflow.add_conditional_edges(
        "increment_attempt_combined",
        lambda state: "process_combined" if state['needs_section_rerun']['combined'] and state['section_attempts'].get('combined', 0) < state['max_attempts'] else "process_country",
        {
            "process_combined": "process_combined",
            "process_country": "process_country"
        }
    )
    
    # Add country analysis flow
    workflow.add_edge("process_country", "validate_country")
    workflow.add_conditional_edges(
        "validate_country",
        lambda state: "increment_attempt_country" if not state['validation_passed'] and state['needs_section_rerun']['country'] else "process_personas",
        {
            "increment_attempt_country": "increment_attempt_country",
            "process_personas": "process_personas"
        }
    )
    
    workflow.add_conditional_edges(
        "increment_attempt_country",
        lambda state: "process_country" if state['needs_section_rerun']['country'] and state['section_attempts'].get('country', 0) < state['max_attempts'] else "process_personas",
        {
            "process_country": "process_country",
            "process_personas": "process_personas"
        }
    )
    
    # Add persona analysis flow
    workflow.add_edge("process_personas", "validate_personas")
    workflow.add_conditional_edges(
        "validate_personas",
        lambda state: "increment_attempt_personas" if not state['validation_passed'] and any(state['needs_section_rerun'].values()) else "save_report",
        {
            "increment_attempt_personas": "increment_attempt_personas",
            "save_report": "save_report"
        }
    )
    
    workflow.add_conditional_edges(
        "increment_attempt_personas",
        lambda state: "process_section1" if any(state['needs_section_rerun'].values()) and state['section_attempts'].get('personas', 0) < state['max_attempts'] else "save_report",
        {
            "process_section1": "process_section1",
            "save_report": "save_report"
        }
    )
    
    # Add final edge
    workflow.add_edge("save_report", END)
    
    # Compile and run graph with increased recursion limit
    app = workflow.compile()
    config = RunnableConfig(recursion_limit=50)
    result = app.invoke(initial_state, config=config)
    
    return result

if __name__ == "__main__":
    main()
