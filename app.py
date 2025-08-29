import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import sys
import importlib.util

# Add utils to path
sys.path.append('utils')

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Brand Response | Customer Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4F46E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .step-container {
        background: #F8F9FA;
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #4F46E5;
        margin: 1rem 0;
    }
    
    .insight-box {
        background: #F0F4FF;
        border: 1px solid #C7D2FE;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #4F46E5;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<div class="main-header">Brand Response</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Customer Intelligence Platform</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'client_data' not in st.session_state:
        st.session_state.client_data = None
    if 'business_context' not in st.session_state:
        st.session_state.business_context = {}
    if 'selected_variables' not in st.session_state:
        st.session_state.selected_variables = []
    if 'enriched_data' not in st.session_state:
        st.session_state.enriched_data = None
    if 'insights' not in st.session_state:
        st.session_state.insights = {}

    # Sidebar navigation
    st.sidebar.title("Process Steps")
    
    steps = [
        "Upload Client Data",
        "Business Context", 
        "AI Variable Selection",
        "Data Enrichment",
        "Generate Insights",
        "Export Report"
    ]
    
    # Show current step with navigation
    for i, step_name in enumerate(steps, 1):
        if i == st.session_state.step:
            st.sidebar.markdown(f"**→ {step_name}**")
        elif i < st.session_state.step:
            # Allow clicking on completed steps
            if st.sidebar.button(f"✅ {step_name}", key=f"nav_{i}"):
                st.session_state.step = i
                st.rerun()
        else:
            st.sidebar.markdown(f"> {step_name}")
    
    # Add some spacing
    st.sidebar.markdown("---")
    
    # Debug info
    if st.sidebar.checkbox("Show Debug Info"):
        st.sidebar.write("**Current Step:**", st.session_state.step)
        st.sidebar.write("**Has Client Data:**", st.session_state.client_data is not None)
        st.sidebar.write("**Has Business Context:**", bool(st.session_state.business_context))
        st.sidebar.write("**Selected Variables:**", len(st.session_state.selected_variables))
    
    # Reset button
    if st.sidebar.button("🔄 Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Allow clicking on completed steps to navigate back

    # Main content based on step
    if st.session_state.step == 1:
        show_data_upload()
    elif st.session_state.step == 2:
        show_business_context()
    elif st.session_state.step == 3:
        show_variable_selection()
    elif st.session_state.step == 4:
        show_data_enrichment()
    elif st.session_state.step == 5:
        show_insights_generation()
    elif st.session_state.step == 6:
        show_report_export()

def show_data_upload():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.header("Step 1: Upload Client Data")
    st.markdown("Upload your client's customer data (CSV format). We'll use this as the foundation for our analysis.")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload a CSV file with customer data including emails, names, addresses, phone numbers, etc."
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.client_data = df
            
            st.success(f"✅ Successfully loaded {len(df)} records!")
            
            # Show preview
            st.subheader("Data Preview")
            st.dataframe(df.head(10), width=1000)
            
            # Show column info
            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': [str(dtype) for dtype in df.dtypes],  # Convert to string to avoid Arrow issues
                'Non-Null Count': df.count(),
                'Sample Value': [str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A' for col in df.columns]
            })
            st.dataframe(col_info, width=1000)
            
            if st.button("Continue to Business Context →", type="primary"):
                st.session_state.step = 2
                st.rerun()
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    else:
        # Show sample data option
        st.info("💡 **Don't have data ready?** Try our sample dataset to explore the platform.")
        if st.button("Load Sample Coffee Shop Data"):
            # Create sample data
            sample_data = create_sample_data()
            st.session_state.client_data = sample_data
            st.success("✅ Sample data loaded!")
            # Auto advance to show the data
            st.rerun()
    
    # Show continue button if data is loaded (outside the else block)
    if st.session_state.client_data is not None and not uploaded_file:
        st.subheader("Sample Data Preview")
        st.dataframe(st.session_state.client_data.head(10), width=1000)
        
        # Show column info
        st.subheader("Column Information")
        df = st.session_state.client_data
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': [str(dtype) for dtype in df.dtypes],  # Convert to string
            'Non-Null Count': df.count(),
            'Sample Value': [str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A' for col in df.columns]
        })
        st.dataframe(col_info, width=1000)
        
        if st.button("Continue to Business Context →", type="primary", key="continue_from_sample"):
            st.session_state.step = 2
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_business_context():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.header("🏢 Step 2: Business Context")
    st.markdown("Tell us about the business so we can select the most relevant data variables for analysis.")
    
    with st.form("business_context_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input("Business Name", placeholder="e.g., Roasted Bean Coffee Co.")
            industry = st.selectbox(
                "Industry",
                ["Food & Beverage", "Retail", "Professional Services", "Healthcare", "Technology", "Real Estate", "Other"]
            )
            business_model = st.selectbox(
                "Business Model",
                ["B2C Retail", "B2B Services", "Subscription", "Marketplace", "SaaS", "Other"]
            )
        
        with col2:
            target_customer = st.text_area(
                "Who do you think your customers are?",
                placeholder="e.g., Young professionals, ages 25-40, urban, tech-savvy, values convenience...",
                height=100
            )
            brand_positioning = st.text_area(
                "How do you currently position your brand?",
                placeholder="e.g., Premium artisanal coffee for discerning professionals...",
                height=100
            )
        
        goals = st.multiselect(
            "What are your main goals for this analysis?",
            [
                "Understand customer demographics",
                "Identify market positioning opportunities", 
                "Optimize marketing messaging",
                "Competitive differentiation"
            ]
        )
        
        additional_context = st.text_area(
            "Additional Context (Optional)",
            placeholder="Any other relevant information about your business, customers, or market...",
            height=80
        )
        
        submitted = st.form_submit_button("Continue to Variable Selection →", type="primary")
        
        if submitted:
            st.session_state.business_context = {
                'business_name': business_name,
                'industry': industry,
                'business_model': business_model,
                'target_customer': target_customer,
                'brand_positioning': brand_positioning,
                'goals': goals,
                'additional_context': additional_context
            }
            st.session_state.step = 3
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_variable_selection():
    st.header("🤖 Step 3: Data Enhancement Selection")
    st.markdown("Analyzing your business context to select the most strategic data variables...")
    
    # Show business context summary
    if st.session_state.business_context:
        with st.expander("Business Context Summary", expanded=False):
            for key, value in st.session_state.business_context.items():
                if value and key != 'goals':
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                elif key == 'goals' and value:
                    st.write(f"**Goals:** {', '.join(value)}")
    
    if st.button("🤖 Generate Enhancement Recommendations", type="primary"):
        with st.spinner("Analyzing your business context..."):
            try:
                # Import the AI helper
                from utils.ai_helper import select_variables_with_ai
                
                selected_vars = select_variables_with_ai(st.session_state.business_context)
                st.session_state.selected_variables = selected_vars
                
                st.success("✅ Here are the selected variables optimized for your business!")
                
                # Show selected variables with AI explanations
                show_ai_variable_explanations(selected_vars)
                
            except Exception as e:
                st.error(f"AI selection failed: {str(e)}")
                st.info("Using fallback variable selection...")
                # Fallback to mock selection
                recommended_vars = [
                    {"variable": "AGE", "rationale": "Core demographic for market segmentation", "category": "demographics"},
                    {"variable": "INCOME_HH", "rationale": "Essential for pricing strategy", "category": "economic"},
                    {"variable": "EDUCATION", "rationale": "Indicates customer sophistication", "category": "lifestyle"}
                ]
                st.session_state.selected_variables = recommended_vars
                show_ai_variable_explanations(recommended_vars)
    
    # Show continue button if variables are selected
    if st.session_state.selected_variables:
        if st.button("Continue to Data Enrichment →", type="primary"):
            st.session_state.step = 4
            st.rerun()

def show_ai_variable_explanations(variables):
    """Display AI-selected variables with their strategic rationale"""
    st.subheader("Recommended Variables & Strategic Rationale")
    
    # Group by category
    by_category = {}
    for var in variables:
        category = var.get('category', 'other')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(var)
    
    # Display by category
    category_icons = {
        'demographics': '👥',
        'economic': '💰', 
        'lifestyle': '🏠',
        'interests': '🎯',
        'shopping': '🛍️',
        'media': '📺'
    }
    
    for category, vars_in_category in by_category.items():
        icon = category_icons.get(category, '📊')
        st.markdown(f"**{icon} {category.upper()}**")
        for var in vars_in_category:
            st.markdown(f"• **{var['variable']}**: {var['rationale']}")
        st.markdown("")  # spacing

def show_data_enrichment():
    st.header("⚡ Step 4: Data Enrichment")
    st.markdown("Connecting to identity graph and enriching your customer data...")
    
    # Show selected variables summary
    if st.session_state.selected_variables:
        st.subheader("🎯 Selected Variables for Enrichment")
        for var in st.session_state.selected_variables[:5]:  # Show first 5
            st.markdown(f"• **{var['variable']}**: {var['rationale'][:100]}...")
        if len(st.session_state.selected_variables) > 5:
            st.markdown(f"*... and {len(st.session_state.selected_variables) - 5} more variables*")
    
    if st.button("🚀 Start Data Enrichment", type="primary"):
        with st.spinner("Enriching data via Brand Response graph..."):
            import time
            time.sleep(2)
            
            try:
                # Load the real enriched data
                import os
                data_path = "data/sample_enriched_data.csv"
                if os.path.exists(data_path):
                    enriched_df = pd.read_csv(data_path)
                    st.session_state.enriched_data = enriched_df
                    
                    st.success("✅ Data enrichment complete!")
                    
                    # Show enrichment results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Records Processed", f"{len(st.session_state.client_data):,}")
                    with col2:
                        st.metric("Variables Added", f"{len(st.session_state.selected_variables)}")
                    with col3:
                        match_rate = min(len(enriched_df), len(st.session_state.client_data)) / len(st.session_state.client_data)
                        st.metric("Match Rate", f"{match_rate:.1%}")
                    
                    # Show sample of enriched data
                    st.subheader("📊 Enriched Data Preview")
                    st.markdown("Your customer data has been enhanced with strategic variables from our data sources:")
                    
                    # Show relevant columns
                    display_columns = ['FIRST_NAME', 'LAST_NAME', 'AGE', 'INCOME_HH', 'EDUCATION', 'URBANICITY', 'GOURMET_AFFINITY']
                    available_columns = [col for col in display_columns if col in enriched_df.columns]
                    if available_columns:
                        st.dataframe(enriched_df[available_columns].head(10), width=1000)
                    else:
                        st.dataframe(enriched_df.head(10), width=1000)
                    
                else:
                    # Fallback if file not found
                    st.warning("Sample enriched data file not found. Using mock data...")
                    st.session_state.enriched_data = "mock_enriched"
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Records Processed", f"{len(st.session_state.client_data):,}")
                    with col2:
                        st.metric("Variables Added", f"{len(st.session_state.selected_variables)}")
                    with col3:
                        st.metric("Match Rate", "87.3%")
                
            except Exception as e:
                st.error(f"Enrichment failed: {str(e)}")
                st.info("Please ensure sample_enriched_data.csv is in the data/ folder")
    
    # Show continue button outside the enrichment block if data exists
    if st.session_state.enriched_data is not None:
        st.markdown("---")
        if st.button("Continue to Insights Generation →", type="primary", key="continue_to_insights"):
            st.session_state.step = 5
            st.rerun()

def show_insights_generation():
    st.header("📈 Step 5: Generate Customer Intelligence")
    st.markdown("Analyzing enriched customer data to generate strategic insights...")
    
    # Show data summary
    if hasattr(st.session_state, 'enriched_data') and isinstance(st.session_state.enriched_data, pd.DataFrame):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Records Analyzed", f"{len(st.session_state.enriched_data):,}")
        with col2:
            st.metric("Variables Used", f"{len(st.session_state.selected_variables)}")
        with col3:
            st.metric("Analysis Depth", "Strategic")
    
    if st.button("🧠 Generate Insights", type="primary"):
        with st.spinner("Analyzing patterns and generating strategic insights..."):
            import time
            time.sleep(3)
            
            try:
                # Import the AI helper
                from utils.ai_helper import generate_customer_insights
                
                insights = generate_customer_insights(
                    st.session_state.enriched_data, 
                    st.session_state.business_context, 
                    st.session_state.selected_variables
                )
                st.session_state.insights = insights
                
                st.success("✅ Customer intelligence analysis complete!")
                
                display_insights(insights)
                
            except Exception as e:
                st.error(f"Insights generation failed: {str(e)}")
                # Fallback to basic insights
                insights = {
                    "executive_summary": "Customer analysis completed with available data.",
                    "key_findings": ["Analysis based on enriched customer data", "Insights generated from selected variables"],
                    "segments": {"Primary": {"percentage": 100, "profile": "All analyzed customers"}},
                    "recommendations": ["Continue data collection for deeper insights"]
                }
                st.session_state.insights = insights
                display_insights(insights)
    
    # Show continue button if insights are generated
    if st.session_state.insights:
        if st.button("Continue to Export Report →", type="primary"):
            st.session_state.step = 6
            st.rerun()

def show_report_export():
    st.header("📄 Step 6: Export Customer Intelligence Report")
    st.markdown("Your customer intelligence analysis is complete!")
    
    if st.session_state.insights:
        # Display the insights one more time
        display_insights(st.session_state.insights)
        
        st.markdown("---")
        st.subheader("📥 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create text summary for download
            report_text = generate_text_report()
            st.download_button(
                label="📄 Download Text Report",
                data=report_text,
                file_name=f"{st.session_state.business_context.get('business_name', 'Customer')}_Intelligence_Report.txt",
                mime="text/plain"
            )
        
        with col2:
            # JSON export for further analysis
            import json
            report_data = {
                'business_context': st.session_state.business_context,
                'selected_variables': st.session_state.selected_variables,
                'insights': st.session_state.insights,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            st.download_button(
                label="📊 Download JSON Data",
                data=json.dumps(report_data, indent=2),
                file_name=f"{st.session_state.business_context.get('business_name', 'Customer')}_Analysis_Data.json",
                mime="application/json"
            )
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Start New Analysis", type="secondary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("🎯 Refine Analysis", type="secondary"):
                st.session_state.step = 3  # Go back to variable selection
                st.rerun()

def generate_text_report():
    """Generate a formatted text report"""
    business_name = st.session_state.business_context.get('business_name', 'Your Business')
    insights = st.session_state.insights
    
    report = f"""
CUSTOMER INTELLIGENCE REPORT
{business_name}
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

=====================================
EXECUTIVE SUMMARY
=====================================
{insights.get('executive_summary', '')}

=====================================
KEY FINDINGS
=====================================
"""
    
    for i, finding in enumerate(insights.get('key_findings', []), 1):
        report += f"{i}. {finding}\n"
    
    if 'demographic_surprises' in insights:
        report += f"""
=====================================
DEMOGRAPHIC SURPRISES
=====================================
"""
        for surprise in insights['demographic_surprises']:
            report += f"• {surprise}\n"
    
    report += f"""
=====================================
CUSTOMER SEGMENTS
=====================================
"""
    
    for segment, details in insights.get('segments', {}).items():
        report += f"{segment} ({details.get('percentage', 0)}%)\n"
        report += f"Profile: {details.get('profile', '')}\n\n"
    
    report += f"""
=====================================
STRATEGIC RECOMMENDATIONS
=====================================
"""
    
    for i, rec in enumerate(insights.get('recommendations', []), 1):
        report += f"{i}. {rec}\n"
    
    report += f"""
=====================================
ANALYSIS DETAILS
=====================================
Variables Analyzed: {len(st.session_state.selected_variables)}
Records Processed: {len(st.session_state.enriched_data) if isinstance(st.session_state.enriched_data, pd.DataFrame) else 'N/A'}

Selected Variables:
"""
    
    for var in st.session_state.selected_variables:
        report += f"• {var['variable']}: {var['rationale']}\n"
    
    report += f"""

=====================================
Brand Response Customer Intelligence Platform
=====================================
"""
    
    return report

def create_sample_data():
    """Create sample coffee shop customer data"""
    import random
    
    first_names = ["John", "Sarah", "Michael", "Emma", "David", "Lisa", "Chris", "Anna"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    
    data = []
    for i in range(500):
        first = random.choice(first_names)
        last = random.choice(last_names)
        data.append({
            'customer_id': f'CUST_{i+1:04d}',
            'first_name': first,
            'last_name': last,
            'email': f"{first.lower()}.{last.lower()}@{random.choice(domains)}",
            'phone': f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
            'city': random.choice(['Seattle', 'Portland', 'San Francisco', 'Denver']),
            'state': random.choice(['WA', 'OR', 'CA', 'CO']),
            'zip': f"{random.randint(90000, 99999)}"
        })
    
    return pd.DataFrame(data)

def generate_mock_insights():
    """Generate mock insights for demo"""
    return {
        'executive_summary': "Your customer base is significantly older and more affluent than your current brand positioning targets, creating immediate opportunities for messaging refinement and premium positioning.",
        'key_findings': [
            "78% of customers are aged 30-60, broader than assumed 25-40 target",
            "Median household income is $78,000 vs assumed $55,000 (42% higher)",
            "43% college-educated vs 28% assumed - more sophisticated audience",
            "73% show premium product affinity - quality over convenience preference"
        ],
        'segments': {
            'Affluent Empty Nesters': {'percentage': 39, 'profile': 'Age 45-60, HHI $85K+, no children at home'},
            'Educated Suburbanites': {'percentage': 32, 'profile': 'Age 35-50, college educated, families'},
            'Quality-First Professionals': {'percentage': 29, 'profile': 'Age 30-45, white-collar careers'}
        }
    }

def display_insights(insights):
    """Display the generated insights in a professional format"""
    
    # Executive Summary
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.subheader("🎯 Executive Summary")
    st.markdown(insights.get('executive_summary', ''))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Key Findings
    st.subheader("📊 Key Findings")
    findings = insights.get('key_findings', [])
    for i, finding in enumerate(findings, 1):
        st.markdown(f"**{i}.** {finding}")
    
    # Demographic Surprises (if available)
    if 'demographic_surprises' in insights:
        st.subheader("🔍 Demographic Surprises")
        for surprise in insights['demographic_surprises']:
            st.markdown(f"• {surprise}")
    
    # Customer Segments
    st.subheader("👥 Customer Segments")
    segments = insights.get('segments', {})
    
    if segments:
        # Create segment visualization
        segment_data = []
        for segment_name, details in segments.items():
            segment_data.append({
                'Segment': segment_name,
                'Percentage': details.get('percentage', 0),
                'Profile': details.get('profile', '')
            })
        
        # Display as columns
        cols = st.columns(len(segment_data))
        for i, (col, segment) in enumerate(zip(cols, segment_data)):
            with col:
                st.metric(
                    segment['Segment'], 
                    f"{segment['Percentage']}%",
                    help=segment['Profile']
                )
                st.caption(segment['Profile'])
    
    # Raw Statistics (if available)
    if 'raw_stats' in insights and insights['raw_stats']:
        with st.expander("📈 Data Statistics", expanded=False):
            stats = insights['raw_stats']
            
            col1, col2 = st.columns(2)
            with col1:
                if 'age_median' in stats:
                    st.metric("Median Age", f"{stats['age_median']:.1f} years")
                if 'high_income_percent' in stats:
                    st.metric("High Income (>$150K)", f"{stats['high_income_percent']:.1f}%")
            
            with col2:
                if 'college_plus_percent' in stats:
                    st.metric("College+ Education", f"{stats['college_plus_percent']:.1f}%")
                if 'urban_percent' in stats:
                    st.metric("Urban Customers", f"{stats['urban_percent']:.1f}%")
    
    # Recommendations
    st.subheader("💡 Strategic Recommendations")
    recommendations = insights.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")
    
    # Action Items
    if recommendations:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.subheader("⚡ Next Steps")
        st.markdown("**Immediate Actions:**")
        for rec in recommendations[:3]:  # Show top 3 as immediate actions
            st.markdown(f"• {rec}")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()