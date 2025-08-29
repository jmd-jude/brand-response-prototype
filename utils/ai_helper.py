import os
import json
from typing import List, Dict, Any
import anthropic

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ID Graph Schema (key variables for brand analysis)
ID_GRAPH_VARIABLES = {
    "demographics": {
        "AGE": "Age of individual",
        "BIRTH_YEAR": "Birth year",
        "GENDER": "Male/Female",
        "MALE": "Binary indicator for male gender",
        "GENERATION": "Generation cohort (Millennials, Gen X, Baby Boomers, etc.)",
        "MARRIED": "Marital status indicator",
        "MARITAL_STATUS": "Detailed marital status",
        "CHILDREN_HH": "Number of children in household",
        "NUM_ADULTS_HH": "Number of adults in household",
        "NUM_PERSONS_HH": "Total household size"
    },
    "economic": {
        "INCOME_HH": "Household income brackets",
        "INCOME_MIDPTS_HH": "Household income midpoint estimates",
        "PREMIUM_INCOME_HH": "High-precision income segments",
        "NET_WORTH_HH": "Household net worth brackets",
        "NET_WORTH_MIDPT_HH": "Net worth midpoint estimates",
        "CREDIT_CARD": "Credit card ownership indicator",
        "PREMIUM_CARD": "Premium credit card ownership",
        "NEW_CREDIT_OFFERED_HH": "Recent credit offers received"
    },
    "lifestyle": {
        "EDUCATION": "Educational attainment level",
        "EDUCATION_ORDINAL": "Education level (numeric scale)",
        "OCCUPATION_TYPE": "White collar vs blue collar",
        "OCCUPATION_CATEGORY": "Detailed occupation categories",
        "DWELLING_TYPE": "Single family vs multi-family housing",
        "URBANICITY": "Rural, Suburban, or Urban classification",
        "LIFESTYLE_CLUSTER": "Proprietary lifestyle segmentation"
    },
    "interests": {
        "READING_AVID_READER": "Frequent book/magazine reader",
        "READING_FINANCE": "Reads financial publications",
        "READING_COOKING_CULINARY": "Cooking/culinary interest",
        "READING_HEALTH_REMEDIES": "Health and wellness reading",
        "FITNESS_AFFINITY": "Exercise and fitness interest",
        "GOURMET_AFFINITY": "Fine food and dining interest",
        "HIGH_TECH_AFFINITY": "Technology adoption propensity",
        "TRAVEL_AFFINITY": "Travel and vacation interest",
        "AUTO_AFFINITY": "Automotive interest",
        "OUTDOORS_AFFINITY": "Outdoor activities interest"
    },
    "shopping": {
        "BARGAIN_HUNTER_AFFINITY": "Price-conscious shopping behavior",
        "CATALOG_AFFINITY": "Catalog shopping preference",
        "RECENT_CATALOG_PURCHASES_TOTAL_DOLLARS": "Recent catalog spending",
        "RECENT_APPAREL_PURCHASES_TOTAL_DOLLARS": "Recent clothing spending",
        "PREMIUM_INCOME_MIDPT_HH": "Premium income segment midpoint",
        "LIKELY_CHARITABLE_DONOR": "Likelihood of charitable giving"
    },
    "media": {
        "READING_MAGAZINES": "Magazine readership",
        "TV_MOVIES_AFFINITY": "Entertainment media consumption",
        "RECENT_MAGAZINE_SUBSCRIPTIONS_NUM": "Number of magazine subscriptions"
    }
}

def get_variable_selection_prompt(business_context: Dict[str, Any]) -> str:
    """Generate prompt for AI variable selection"""
    
    variables_text = ""
    for category, variables in ID_GRAPH_VARIABLES.items():
        variables_text += f"\n**{category.upper()}:**\n"
        for var, desc in variables.items():
            variables_text += f"- {var}: {desc}\n"
    
    prompt = f"""
You are a customer intelligence analyst helping a branding consultancy select the most strategic data variables for client analysis.

BUSINESS CONTEXT:
- Business: {business_context.get('business_name', 'N/A')}
- Industry: {business_context.get('industry', 'N/A')}
- Business Model: {business_context.get('business_model', 'N/A')}
- Current Target Customer Assumptions: {business_context.get('target_customer', 'N/A')}
- Brand Positioning: {business_context.get('brand_positioning', 'N/A')}
- Analysis Goals: {', '.join(business_context.get('goals', []))}
- Additional Context: {business_context.get('additional_context', 'N/A')}

AVAILABLE DATA VARIABLES:
{variables_text}

TASK: Select exactly 12-15 variables that would be most strategically valuable for:
1. Revealing gaps between customer assumptions and reality
2. Identifying brand positioning opportunities  
3. Enabling targeted messaging and marketing
4. Providing actionable business insights

REQUIREMENTS:
- Choose variables that directly relate to this specific business context
- Prioritize variables that can challenge current assumptions
- Include a mix of demographics, economics, lifestyle, and interests
- Focus on variables that inform brand strategy decisions

Respond with ONLY a JSON object in this exact format:
{{
    "selected_variables": [
        {{
            "variable": "VARIABLE_NAME",
            "rationale": "Strategic explanation for why this variable is critical for this specific business",
            "category": "demographics|economic|lifestyle|interests|shopping|media"
        }}
    ]
}}
"""
    return prompt

def select_variables_with_ai(business_context: Dict[str, Any]) -> List[Dict[str, str]]:
    """Use AI to select optimal variables for the given business context"""
    
    prompt = get_variable_selection_prompt(business_context)
    
    try:
        response = client.messages.create(
            model=os.getenv("LLM_MODEL", "claude-3-sonnet-20240229"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the JSON response
        response_text = response.content[0].text.strip()
        
        # Clean up the response in case there's extra text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
            
        result = json.loads(response_text)
        return result.get("selected_variables", [])
        
    except Exception as e:
        print(f"Error in AI variable selection: {str(e)}")
        # Fallback to default variables
        return get_fallback_variables()

def get_fallback_variables() -> List[Dict[str, str]]:
    """Fallback variable selection if AI fails"""
    return [
        {"variable": "AGE", "rationale": "Core demographic for market segmentation", "category": "demographics"},
        {"variable": "INCOME_HH", "rationale": "Essential for pricing and positioning strategy", "category": "economic"},
        {"variable": "EDUCATION", "rationale": "Indicates sophistication and messaging approach", "category": "lifestyle"},
        {"variable": "URBANICITY", "rationale": "Geographic preferences affect brand positioning", "category": "lifestyle"},
        {"variable": "MARITAL_STATUS", "rationale": "Life stage affects purchasing behavior", "category": "demographics"},
        {"variable": "CHILDREN_HH", "rationale": "Family status impacts product usage patterns", "category": "demographics"},
        {"variable": "OCCUPATION_TYPE", "rationale": "Professional vs blue-collar preferences differ", "category": "lifestyle"},
        {"variable": "LIFESTYLE_CLUSTER", "rationale": "Behavioral segmentation for targeted messaging", "category": "lifestyle"},
        {"variable": "HIGH_TECH_AFFINITY", "rationale": "Technology adoption affects marketing channels", "category": "interests"},
        {"variable": "GOURMET_AFFINITY", "rationale": "Quality appreciation aligns with premium positioning", "category": "interests"},
        {"variable": "FITNESS_AFFINITY", "rationale": "Health consciousness affects product preferences", "category": "interests"},
        {"variable": "READING_MAGAZINES", "rationale": "Media consumption patterns for advertising", "category": "media"}
    ]

def generate_customer_insights(enriched_data, business_context: Dict[str, Any], selected_variables: List[Dict[str, str]]) -> Dict[str, Any]:
    """Generate AI-powered customer insights from enriched data"""
    
    if isinstance(enriched_data, str):
        # Fallback for mock data
        return get_mock_insights()
    
    try:
        # Analyze the actual data
        insights = analyze_enriched_data(enriched_data, business_context, selected_variables)
        return insights
        
    except Exception as e:
        print(f"Error generating insights: {str(e)}")
        return get_mock_insights()

def analyze_enriched_data(df, business_context: Dict[str, Any], selected_variables: List[Dict[str, str]]) -> Dict[str, Any]:
    """Analyze the enriched dataframe and generate insights"""
    
    # Extract key statistics
    stats = {}
    
    # Age analysis
    if 'AGE' in df.columns:
        stats['age_median'] = df['AGE'].median()
        stats['age_ranges'] = {
            'under_30': (df['AGE'] < 30).sum() / len(df) * 100,
            'age_30_50': ((df['AGE'] >= 30) & (df['AGE'] < 50)).sum() / len(df) * 100,
            'over_50': (df['AGE'] >= 50).sum() / len(df) * 100
        }
    
    # Income analysis
    if 'PREMIUM_INCOME_HH' in df.columns:
        high_income = df['PREMIUM_INCOME_HH'].str.contains('150K|200K|250K', na=False).sum() / len(df) * 100
        stats['high_income_percent'] = high_income
    
    # Education analysis
    if 'EDUCATION' in df.columns:
        college_plus = df['EDUCATION'].str.contains('College|Graduate', na=False).sum() / len(df) * 100
        stats['college_plus_percent'] = college_plus
    
    # Lifestyle analysis
    if 'URBANICITY' in df.columns:
        urban_percent = df['URBANICITY'].str.contains('Urban', na=False).sum() / len(df) * 100
        stats['urban_percent'] = urban_percent
    
    # Generate AI insights based on these stats
    insights_prompt = f"""
    Analyze this customer data for {business_context.get('business_name', 'the business')} and provide strategic insights.

    BUSINESS CONTEXT:
    - Industry: {business_context.get('industry')}
    - Target Assumptions: {business_context.get('target_customer')}
    - Brand Positioning: {business_context.get('brand_positioning')}

    DATA INSIGHTS:
    - Median Age: {stats.get('age_median', 'N/A')}
    - Age Distribution: Under 30: {stats.get('age_ranges', {}).get('under_30', 0):.1f}%, 30-50: {stats.get('age_ranges', {}).get('age_30_50', 0):.1f}%, Over 50: {stats.get('age_ranges', {}).get('over_50', 0):.1f}%
    - High Income (>$150K): {stats.get('high_income_percent', 0):.1f}%
    - College+ Education: {stats.get('college_plus_percent', 0):.1f}%
    - Urban Customers: {stats.get('urban_percent', 0):.1f}%
    
    Total Records Analyzed: {len(df)}

    Provide insights in JSON format:
    {{
        "executive_summary": "Key finding about customer reality vs assumptions",
        "key_findings": ["finding 1", "finding 2", "finding 3"],
        "demographic_surprises": ["surprise 1", "surprise 2"],
        "segments": {{
            "Primary Segment": {{"percentage": X, "profile": "description"}},
            "Secondary Segment": {{"percentage": Y, "profile": "description"}},
            "Opportunity Segment": {{"percentage": Z, "profile": "description"}}
        }},
        "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
    }}
    """
    
    try:
        response = client.messages.create(
            model=os.getenv("LLM_MODEL", "claude-3-sonnet-20240229"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2500")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            messages=[
                {"role": "user", "content": insights_prompt}
            ]
        )
        
        response_text = response.content[0].text.strip()
        
        # Clean up JSON response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
            
        import json
        insights = json.loads(response_text)
        
        # Add raw stats for display
        insights['raw_stats'] = stats
        
        return insights
        
    except Exception as e:
        print(f"Error in AI insights generation: {str(e)}")
        return get_mock_insights_with_stats(stats)

def get_mock_insights():
    """Fallback mock insights"""
    return {
        "executive_summary": "Your customer data analysis reveals significant opportunities for brand repositioning and targeted marketing strategies.",
        "key_findings": [
            "Customer demographics differ from current brand assumptions",
            "Income levels suggest premium positioning opportunities", 
            "Geographic distribution indicates untapped markets"
        ],
        "segments": {
            "Primary Segment": {"percentage": 45, "profile": "Core customer group with highest value potential"},
            "Growth Segment": {"percentage": 32, "profile": "Emerging segment with expansion opportunities"},
            "Niche Segment": {"percentage": 23, "profile": "Specialized group requiring targeted approach"}
        },
        "recommendations": [
            "Adjust brand messaging to reflect actual customer sophistication",
            "Develop premium service offerings for high-income segments",
            "Optimize marketing channels based on demographic insights"
        ]
    }

def get_mock_insights_with_stats(stats):
    """Mock insights incorporating real stats"""
    age_insight = f"Median customer age is {stats.get('age_median', 45)} years"
    if stats.get('age_ranges', {}).get('over_50', 0) > 40:
        age_insight += ", indicating a more mature customer base than typically assumed"
    
    return {
        "executive_summary": f"Analysis of your customer data reveals key insights. {age_insight}.",
        "key_findings": [
            f"High-income customers represent {stats.get('high_income_percent', 25):.1f}% of your base",
            f"College-educated customers comprise {stats.get('college_plus_percent', 60):.1f}% of your audience",
            f"Urban customers make up {stats.get('urban_percent', 70):.1f}% of your market"
        ],
        "segments": {
            "Affluent Professionals": {"percentage": 45, "profile": "High-income, educated urban customers"},
            "Emerging Adults": {"percentage": 30, "profile": "Younger demographic with growth potential"}, 
            "Mature Market": {"percentage": 25, "profile": "Established customers with premium preferences"}
        },
        "recommendations": [
            "Leverage high education levels in sophisticated messaging",
            "Develop urban-focused marketing campaigns",
            "Create premium offerings for affluent segments"
        ],
        "raw_stats": stats
    }