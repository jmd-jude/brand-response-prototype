import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

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
        font-size: 1.2rem;
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
        "📊 Upload Client Data",
        "🏢 Business Context", 
        "🤖 AI Variable Selection",
        "⚡ Data Enrichment",
        "📈 Generate Insights",
        "📄 Export Report"
    ]
    
    # Show current step
    for i, step_name in enumerate(steps, 1):
        if i == st.session_state.step:
            st.sidebar.markdown(f"**→ {step_name}**")
        elif i < st.session_state.step:
            st.sidebar.markdown(f"✅ {step_name}")
        else:
            st.sidebar.markdown(f"⏳ {step_name}")
    
    # Reset button
    if st.sidebar.button("🔄 Start Over"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    
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
    st.header("📊 Step 1: Upload Client Data")
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
            st.dataframe(df.head(10), use_container_width=True)
            
            # Show column info
            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes,
                'Non-Null Count': df.count(),
                'Sample Value': [df[col].dropna().iloc[0] if not df[col].dropna().empty else 'N/A' for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)
            
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
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_business_context():
    st.markdown('<div class="step-container">', unsafe_allow_html=True)
    st.header("🏢 Step 2: Business Context")
    st.markdown("Tell us about the business so our AI can select the most relevant data variables for analysis.")
    
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
                "Find new customer segments",
                "Improve targeting efficiency",
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
    st.header("🤖 Step 3: AI Variable Selection")
    st.markdown("Our AI is analyzing your business context to select the most strategic data variables...")
    
    # This is where we'll integrate with OpenAI to select variables
    # For now, we'll show a mock selection
    if st.button("🤖 Generate AI Variable Recommendations", type="primary"):
        with st.spinner("AI analyzing your business context..."):
            # Mock AI selection for now
            import time
            time.sleep(2)
            
            recommended_vars = [
                "AGE", "INCOME_HH", "EDUCATION", "URBANICITY", "MARITAL_STATUS",
                "CHILDREN_HH", "OCCUPATION_TYPE", "PREMIUM_INCOME_HH", 
                "LIFESTYLE_CLUSTER", "COFFEE_AFFINITY", "GOURMET_AFFINITY",
                "FITNESS_AFFINITY", "HIGH_TECH_AFFINITY", "READING_MAGAZINES"
            ]
            
            st.session_state.selected_variables = recommended_vars
            
            st.success("✅ AI has selected variables optimized for your business!")
            
            # Show selected variables with explanations
            show_variable_explanations(recommended_vars)
            
            if st.button("Continue to Data Enrichment →", type="primary"):
                st.session_state.step = 4
                st.rerun()

def show_variable_explanations(variables):
    st.subheader("Selected Variables & Strategic Rationale")
    
    explanations = {
        "AGE": "Core demographic for coffee preference segmentation",
        "INCOME_HH": "Essential for premium positioning and pricing strategy",
        "EDUCATION": "Correlates with specialty coffee appreciation",
        "URBANICITY": "Urban vs suburban preferences differ significantly",
        "MARITAL_STATUS": "Affects purchasing patterns and consumption habits",
        "CHILDREN_HH": "Family status impacts coffee consumption timing",
        "OCCUPATION_TYPE": "Professional vs blue-collar preferences vary",
        "PREMIUM_INCOME_HH": "Precise income targeting for premium products",
        "LIFESTYLE_CLUSTER": "Behavioral segmentation for targeted messaging",
        "COFFEE_AFFINITY": "Direct relevance to your product category",
        "GOURMET_AFFINITY": "Indicates appreciation for quality/craftsmanship",
        "FITNESS_AFFINITY": "Health-conscious consumers align with premium coffee",
        "HIGH_TECH_AFFINITY": "Tech affinity correlates with coffee shop apps/loyalty",
        "READING_MAGAZINES": "Media consumption patterns for advertising strategy"
    }
    
    for var in variables:
        if var in explanations:
            st.markdown(f"**{var}**: {explanations[var]}")

def show_data_enrichment():
    st.header("⚡ Step 4: Data Enrichment")
    st.markdown("Connecting to identity graph and enriching your customer data...")
    
    if st.button("🚀 Start Data Enrichment", type="primary"):
        with st.spinner("Enriching data via Audience Acuity API..."):
            import time
            time.sleep(3)
            
            # Mock enriched data
            st.session_state.enriched_data = "enriched"  # We'll build this out
            
            st.success("✅ Data enrichment complete!")
            st.info(f"Successfully enriched {len(st.session_state.client_data)} customer records")
            
            if st.button("Continue to Insights Generation →", type="primary"):
                st.session_state.step = 5
                st.rerun()

def show_insights_generation():
    st.header("📈 Step 5: Generate Customer Intelligence")
    st.markdown("Our AI is analyzing your enriched customer data to generate strategic insights...")
    
    if st.button("🧠 Generate AI Insights", type="primary"):
        with st.spinner("AI generating customer intelligence report..."):
            import time
            time.sleep(4)
            
            # Mock insights - we'll make this real with LLM integration
            insights = generate_mock_insights()
            st.session_state.insights = insights
            
            display_insights(insights)
            
            if st.button("Continue to Export Report →", type="primary"):
                st.session_state.step = 6
                st.rerun()

def show_report_export():
    st.header("📄 Step 6: Export Customer Intelligence Report")
    st.markdown("Your customer intelligence analysis is complete!")
    
    if st.session_state.insights:
        display_insights(st.session_state.insights)
        
        st.download_button(
            label="📄 Download PDF Report",
            data="Mock PDF data - we'll implement this",
            file_name="customer_intelligence_report.pdf",
            mime="application/pdf"
        )
        
        if st.button("🔄 Start New Analysis"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

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
    """Display the generated insights"""
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.subheader("🎯 Executive Summary")
    st.markdown(insights['executive_summary'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📊 Key Findings")
    for finding in insights['key_findings']:
        st.markdown(f"• {finding}")
    
    st.subheader("👥 Customer Segments")
    for segment, details in insights['segments'].items():
        st.markdown(f"**{segment}** ({details['percentage']}%): {details['profile']}")

if __name__ == "__main__":
    main()