"""
Test script for country analysis functionality.
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file.")
openai.api_key = OPENAI_API_KEY

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import section summary functions
def import_section_stats_functions():
    from statistical_analysis.Section1.section1_full_stats import get_section1_stats
    from statistical_analysis.Section2.section2_full_stats import get_section2_stats
    from statistical_analysis.Section3.section3_full_stats import get_section3_stats
    from statistical_analysis.Section4.section4_full_stats import get_section4_stats
    return [
        ('Section1', get_section1_stats),
        ('Section2', get_section2_stats),
        ('Section3', get_section3_stats),
        ('Section4', get_section4_stats),
    ]

section_stats_functions = import_section_stats_functions()

# Aggregate demographic data by country from all sections
def aggregate_demographic_by_country(all_section_stats):
    country_data = {}
    for section, section_stats in all_section_stats.items():
        for qkey, summary in section_stats.items():
            demo_summary = summary.get('demographic_analysis')
            if not demo_summary:
                continue
            for country, data in demo_summary.items():
                if country not in country_data:
                    country_data[country] = {}
                country_data[country][f'{section}_{qkey}'] = data
    return country_data

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_insights_for_country(country, country_summary):
    prompt = f"""
You are an expert in API Security analysis. Based on the following demographic data for {country}, generate a concise insight (2-3 sentences) about API Security trends, strengths, or weaknesses for this country. Use the data to highlight any notable patterns or differences.

Demographic Data:
{json.dumps(country_summary, indent=2)}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an expert API Security analyst."},
                  {"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def load_section_stats():
    all_section_stats = {}
    for section, get_stats_func in section_stats_functions:
        try:
            section_stats = get_stats_func()
            all_section_stats[section] = section_stats
        except Exception as e:
            print(f"Warning: Could not load stats for {section}: {e}")
    return all_section_stats

def main():
    # Test loading and print sample demographic summaries
    all_section_stats = load_section_stats()
    print("Aggregating by country...")
    country_data = aggregate_demographic_by_country(all_section_stats)
    print(f"Countries found: {list(country_data.keys())}")
    insights = {}
    print("Generating insights for each country...")
    for country, summary in country_data.items():
        print(f"Generating insight for {country}...")
        insights[country] = generate_insights_for_country(country, summary)
        print(f"Insight for {country}: {insights[country]}")
    # Save insights to file
    output_path = Path("output/country_insights.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(insights, f, indent=2)
    print(f"Insights saved to {output_path}")

if __name__ == "__main__":
    main() 