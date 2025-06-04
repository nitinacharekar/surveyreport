"""
Test script for country analysis functionality.
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import openai
import autogen

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
    return country_data

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_insights_for_country(country, country_summary):
    prompt = f"""
You are an expert in API Security analysis. Based on the following demographic data for {country}, generate a concise insight (2-3 sentences) about API Security trends, strengths, or weaknesses for this country. Use the data to highlight any notable patterns or differences and include precise data points for evidence.

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

def aggregate_country_stats(country_data, exclude_country):
    """
    Aggregate stats for all countries except `exclude_country`.
    Returns a dict in the same format as a single country's entry.
    """
    from collections import defaultdict
    agg = defaultdict(lambda: defaultdict(int))
    for country, qdict in country_data.items():
        if country == exclude_country:
            continue
        for qkey, qstats in qdict.items():
            for stat_key, value in qstats.items():
                if isinstance(value, (int, float)):
                    agg[qkey][stat_key] += value
                else:
                    agg[qkey][stat_key] = value
    return {qkey: dict(stats) for qkey, stats in agg.items()}

def main():
    # Test loading and print sample demographic summaries
    all_section_stats = load_section_stats()
    print("Aggregating by country...")
    country_data = aggregate_demographic_by_country(all_section_stats)
    print(f"Countries found: {list(country_data.keys())}")
    country_outputs = {}
    print("Generating insights for each country...")
    for country, summary in country_data.items():
        print(f"Generating insight for {country}...")
        country_outputs[country] = generate_insights_for_country(country, summary)
        print(f"Insight for {country}: {country_outputs[country]}")

    # --- Country vs Rest Comparison Test ---
    print("\n=== Country vs Rest Comparison Prompts ===")
    for country, summary in country_data.items():
        other_agg = aggregate_country_stats(country_data, country)
        prompt = f"""
Compare the following data for {country} to the aggregate of all other countries. Highlight unique trends, strengths, and weaknesses, and use specific data points.\n\n{country} Data:\n{json.dumps(summary, indent=2)}\n\nAll Other Countries Aggregate:\n{json.dumps(other_agg, indent=2)}\n"""
        print(f"\n--- {country} vs Rest Prompt ---\n{prompt}")

    # Save insights to file
    output_path = Path("output/country_insights.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(country_outputs, f, indent=2)
    print(f"Insights saved to {output_path}")

    # After generating country_outputs, run an AutoGen group chat for discussion and synthesis
    agents = []
    for country in country_outputs:
        agent = autogen.AssistantAgent(
            name=f"{country}_agent",
            system_message=f"You are the API Security analyst for {country}. Your job is to discuss similarities, differences, and unique findings in your country's API security landscape compared to others."
        )
        agents.append(agent)

    moderator = autogen.AssistantAgent(
        name="Moderator",
        system_message="You are a global API Security moderator. Your job is to synthesize the discussion into a comprehensive comparative summary, highlighting global trends, regional differences, and notable outliers."
    )

    groupchat = autogen.GroupChat(agents=agents + [moderator], messages=[], max_round=1)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"api_key": OPENAI_API_KEY, "model": "gpt-4o-mini"})

    # Each agent posts its own analysis
    for country, agent in zip(country_outputs.keys(), agents):
        groupchat.messages.append({
            "role": "assistant",
            "name": agent.name,
            "content": country_outputs[country]
        })

    # Moderator starts the synthesis
    groupchat.messages.append({
        "role": "assistant",
        "name": moderator.name,
        "content": "Please discuss similarities and differences between countries, then synthesize a comparative summary."
    })

    # Run the group chat
    discussion = manager.run()

    # Extract the moderator's final synthesis
    final_comparative = ""
    for msg in groupchat.messages[::-1]:
        if msg["name"] == "Moderator":
            final_comparative = msg["content"]
            break

    print("=== Moderator's Comparative Summary ===")
    print(final_comparative)

if __name__ == "__main__":
    main() 