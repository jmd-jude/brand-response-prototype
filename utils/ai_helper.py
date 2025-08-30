import json
import os
from typing import Dict, List, Any
from anthropic import Anthropic
print(f"API Key loaded: {os.getenv('ANTHROPIC_API_KEY')[:10] if os.getenv('ANTHROPIC_API_KEY') else 'None'}...")

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def load_schema():
    """Load the SIG schema from JSON file"""
    try:
        schema_path = os.path.join('data', 'schema.json')
        with open(schema_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schema: {str(e)}")
        return None

def get_variable_selection_prompt(business_context: Dict[str, Any]) -> str:
    """Generate AI prompt for variable selection with real schema"""
    
    # Load the actual schema
    schema = load_schema()
    
    # Extract available variables from DATA table (main consumer intelligence table)
    available_variables = []
    if schema and 'tables' in schema and 'DATA' in schema['tables']:
        data_fields = schema['tables']['DATA']['fields']
        for field_name, field_info in data_fields.items():
            # Skip internal/technical fields
            if field_name in ['ID', 'ADDRESS_ID', 'HOUSEHOLD_ID', 'SOURCENUMBER', 'NATIONALCONSUMERDATABASE']:
                continue
            
            # Create variable entry with description if available
            var_entry = {
                'name': field_name,
                'type': field_info.get('type', 'UNKNOWN')
            }
            
            # Add description or valid values if available
            if 'description' in field_info:
                var_entry['description'] = field_info['description']
            
            available_variables.append(var_entry)
    
    # Build the variable list text for the prompt
    variables_text = "AVAILABLE VARIABLES FROM IDENTITY GRAPH:\n\n"
    
    # Group by category for better organization
    demographic_vars = []
    economic_vars = []
    lifestyle_vars = []
    interest_vars = []
    behavioral_vars = []
    
    for var in available_variables:
        name = var['name']
        desc = var.get('description', '')
        
        # Categorize variables
        if any(term in name.lower() for term in ['age', 'gender', 'married', 'children', 'generation', 'birth']):
            demographic_vars.append(f"- {name}: {desc}")
        elif any(term in name.lower() for term in ['income', 'credit', 'investment', 'net_worth', 'bank']):
            economic_vars.append(f"- {name}: {desc}")
        elif any(term in name.lower() for term in ['education', 'occupation', 'dwelling', 'urbanicity']):
            lifestyle_vars.append(f"- {name}: {desc}")
        elif '_affinity' in name.lower() or any(term in name.lower() for term in ['reading_', 'music', 'sports', 'travel']):
            interest_vars.append(f"- {name}: {desc}")
        elif any(term in name.lower() for term in ['purchases', 'catalog', 'recent_']):
            behavioral_vars.append(f"- {name}: {desc}")
    
    # Build categorized variable list
    if demographic_vars:
        variables_text += "DEMOGRAPHICS:\n" + "\n".join(demographic_vars[:10]) + "\n\n"
    if economic_vars:
        variables_text += "ECONOMIC:\n" + "\n".join(economic_vars[:8]) + "\n\n"
    if lifestyle_vars:
        variables_text += "LIFESTYLE:\n" + "\n".join(lifestyle_vars[:8]) + "\n\n"
    if interest_vars:
        variables_text += "INTERESTS & AFFINITIES:\n" + "\n".join(interest_vars[:15]) + "\n\n"
    if behavioral_vars:
        variables_text += "PURCHASE BEHAVIOR:\n" + "\n".join(behavioral_vars[:10]) + "\n\n"
    
    prompt = f"""You are a strategic data analyst helping select the most valuable customer intelligence variables for brand strategy.

BUSINESS CONTEXT:
- Industry: {business_context.get('industry', 'Not specified')}
- Target Market: {business_context.get('target_market', 'Not specified')}
- Business Model: {business_context.get('business_model', 'Not specified')}
- Current Challenges: {business_context.get('challenges', 'Not specified')}
- Brand Positioning: {business_context.get('positioning', 'Not specified')}

{variables_text}

YOUR TASK: Select 8-12 variables that will provide the most strategic value for this specific business context.

SELECTION CRITERIA:
1. Choose variables that directly relate to this business context
2. Prioritize variables that can challenge current assumptions about customers
3. Include a strategic mix across different categories
4. Focus on variables that inform brand strategy and positioning decisions
5. Consider variables that reveal unexpected customer segments

RESPOND IN MARKDOWN TABLE FORMAT:

| Variable | Category | Strategic Rationale |
|----------|----------|-------------------|
| VARIABLE_NAME | demographics/economic/lifestyle/interests/behavioral | Specific explanation of why this variable is critical for this business |

Select variables that will reveal the most surprising and actionable insights about who this business's customers really are."""

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
        
        # Parse the markdown table response
        response_text = response.content[0].text.strip()
        
        # Extract table from markdown
        variables = []
        lines = response_text.split('\n')
        in_table = False
        
        for line in lines:
            line = line.strip()
            if '|' in line and not line.startswith('|---'):
                if 'Variable' in line and 'Category' in line and 'Strategic Rationale' in line:
                    in_table = True
                    continue
                elif in_table and line.count('|') >= 3:
                    parts = [part.strip() for part in line.split('|')]
                    if len(parts) >= 4 and parts[1] and parts[2] and parts[3]:
                        variables.append({
                            'variable': parts[1],
                            'category': parts[2],
                            'rationale': parts[3]
                        })
        
        return variables if variables else get_fallback_variables()
        
    except Exception as e:
        print(f"Error in AI variable selection: {str(e)}")
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
        {"variable": "READING_MAGAZINES", "rationale": "Media consumption patterns for advertising", "category": "behavioral"}
    ]

def generate_customer_insights(enriched_data, business_context: Dict[str, Any], selected_variables: List[Dict[str, str]]) -> Dict[str, Any]:
    """Generate AI-powered customer insights from enriched data"""
    
    # Analyze the enriched data
    try:
        # Create summary statistics for each selected variable
        variable_summaries = []
        for var_info in selected_variables:
            var_name = var_info['variable']
            if var_name in enriched_data.columns:
                summary = f"{var_name}: {enriched_data[var_name].value_counts().head().to_dict()}"
                variable_summaries.append(summary)
        
        insights_prompt = f"""Analyze this customer data and generate strategic brand insights.

BUSINESS CONTEXT:
- Industry: {business_context.get('industry', 'Not specified')}
- Target Market: {business_context.get('target_market', 'Not specified')}
- Current Brand Assumptions: {business_context.get('positioning', 'Not specified')}

CUSTOMER DATA ANALYSIS:
{chr(10).join(variable_summaries)}

Generate professional consulting-style insights in this format:

# Executive Summary
[2-3 sentences summarizing the most important findings]

## Key Customer Reality vs. Assumptions
[Table comparing what the business assumed vs what data reveals]

## Strategic Recommendations
1. **Brand Positioning Adjustment**: [Specific recommendation]
2. **Target Audience Refinement**: [Specific recommendation] 
3. **Messaging Strategy**: [Specific recommendation]

## Most Surprising Discovery
[Highlight the most unexpected finding that challenges assumptions]

Write in professional business language suitable for client presentation."""

        response = client.messages.create(
            model=os.getenv("LLM_MODEL", "claude-3-sonnet-20240229"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "3000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            messages=[
                {"role": "user", "content": insights_prompt}
            ]
        )
        
        return {
            'insights_text': response.content[0].text.strip(),
            'variables_analyzed': len(selected_variables),
            'records_analyzed': len(enriched_data)
        }
        
    except Exception as e:
        return {
            'insights_text': f"Error generating insights: {str(e)}",
            'variables_analyzed': 0,
            'records_analyzed': 0
        }