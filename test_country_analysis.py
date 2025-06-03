"""
Test script for country analysis functionality.
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import openai
from statistical_analysis.Section1.section1_full_stats import get_section1_stats
from statistical_analysis.Section2.section2_full_stats import get_section2_stats
from statistical_analysis.Section3.section3_full_stats import get_section3_stats
from statistical_analysis.Section4.section4_full_stats import get_section4_stats

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('country_analysis.log')
    ]
)
logger = logging.getLogger(__name__)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
openai.api_key = OPENAI_API_KEY

def openai_llm(prompt: str) -> str:
    """Generate a response using OpenAI's GPT-4."""
    logger.info(f"Generating response for prompt of length {len(prompt)}")
    client = openai.OpenAI()
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

def process_single_country(country: str, country_data: list) -> tuple[str, str]:
    """Process analysis for a single country."""
    prompt = f"""You are a Country Analyst for {country}. Analyze the following country-specific data 
    across all sections and questions in exactly 2 sentences maximum. Focus only on the most significant trend or insight.
    Compare with overall trends where relevant. Be extremely concise.
    
    Country Data:
    {json.dumps(country_data, indent=2)}"""
    
    return country, openai_llm(prompt)

def process_country_analysis():
    """Process country-specific analyses from all sections."""
    logger.info("Processing country-specific analyses")
    
    # Get all section stats
    all_stats = {
        'section1': get_section1_stats(),
        'section2': get_section2_stats(),
        'section3': get_section3_stats(),
        'section4': get_section4_stats()
    }
    
    # Extract country data from each section
    country_data = {}
    for section, stats in all_stats.items():
        for q_id, q_stats in stats.items():
            if 'demographic_breakdowns' in q_stats and 'Country' in q_stats['demographic_breakdowns']:
                for country_stats in q_stats['demographic_breakdowns']['Country']:
                    country = country_stats['Country']
                    if country not in country_data:
                        country_data[country] = []
                    country_data[country].append({
                        'section': section,
                        'question': q_id,
                        'data': country_stats
                    })
    
    # Process each country's data
    country_analyses = {}
    for country, data in country_data.items():
        country, analysis = process_single_country(country, data)
        country_analyses[country] = analysis
        logger.debug(f"Completed country analysis: {country}")
    
    # Create combined country summary
    country_summarizer_prompt = f"""You are a Country Analysis Moderator. Analyze the country-specific insights from all sections 
    and identify key patterns, differences, and trends across countries in exactly 4 sentences maximum. 
    Highlight any notable regional variations or country-specific challenges. Be extremely concise.
    
    Country Analyses:
    {json.dumps(country_analyses, indent=2)}"""
    
    country_summary = openai_llm(country_summarizer_prompt)
    
    # Save results
    results = {
        "country_analyses": country_analyses,
        "country_summary": country_summary
    }
    
    output_path = 'output/country_analysis.json'
    Path('output').mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Country analysis saved to {output_path}")
    
    return results

if __name__ == "__main__":
    process_country_analysis() 