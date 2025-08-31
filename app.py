import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import sys
from utils.ai_helper import select_variables_with_ai, generate_customer_insights
from utils.logger import SessionLogger

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
    
    # Initialize session state and logger
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
    
    # Initialize logger
    if 'logger' not in st.session_state:
        st.session_state.logger = SessionLogger()

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
        show_generate_insights()
    elif st.session_state.step == 6:
        show_report_export()

def show_data_upload():
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
            
            # Log the data upload
            st.session_state.logger.log_event("data_upload", {
                "records": len(df),
                "columns": len(df.columns),
                "filename": uploaded_file.name,
                "data_source": "uploaded_file"
            })
            
            st.success(f"✅ Successfully loaded {len(df)} records!")
            
            # Show preview
            st.subheader("Data Preview")
            st.dataframe(df.head(10), width=1000)
            
            # Show column info
            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': [str(dtype) for dtype in df.dtypes],
                'Non-Null Count': df.count(),
                'Sample Value': [str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A' for col in df.columns]
            })
            st.dataframe(col_info, width=1000)
            
            if st.button("Continue to Business Context →", type="primary"):
                st.session_state.step = 2
                st.rerun()
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            st.session_state.logger.log_event("data_upload_error", {
                "error": str(e),
                "filename": uploaded_file.name if uploaded_file else "unknown"
            })
    
    else:
        # Show sample data option
        st.info("💡 **Don't have data ready?** Try our sample dataset to explore the platform.")
        if st.button("Load Sample Coffee Shop Data"):
            # Create sample data
            sample_data = create_sample_data()
            st.session_state.client_data = sample_data
            
            # Log sample data loading
            st.session_state.logger.log_event("data_upload", {
                "records": len(sample_data),
                "columns": len(sample_data.columns),
                "filename": "sample_coffee_shop_data",
                "data_source": "sample_generated"
            })
            
            st.success("✅ Sample data loaded!")
            st.rerun()
    
    # Show continue button if data is loaded
    if st.session_state.client_data is not None and not uploaded_file:
        st.subheader("Sample Data Preview")
        st.dataframe(st.session_state.client_data.head(10), width=1000)
        
        # Show column info
        st.subheader("Column Information")
        df = st.session_state.client_data
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': [str(dtype) for dtype in df.dtypes],
            'Non-Null Count': df.count(),
            'Sample Value': [str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A' for col in df.columns]
        })
        st.dataframe(col_info, width=1000)
        
        if st.button("Continue to Business Context →", type="primary", key="continue_from_sample"):
            st.session_state.step = 2
            st.rerun()

def show_business_context():
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
            
            # Log business context capture
            st.session_state.logger.log_event("business_context_captured", {
                "business_name": business_name,
                "industry": industry,
                "business_model": business_model,
                "goals_count": len(goals),
                "has_target_description": len(target_customer) > 0,
                "has_positioning": len(brand_positioning) > 0
            })
            
            st.session_state.step = 3
            st.rerun()

def show_variable_selection():
    st.header("🤖 Step 3: Data Enrichment Selection")
    st.markdown("Analyzing your business context to select the most strategic data variables...")
    
    # Show business context summary
    if st.session_state.business_context:
        with st.expander("Business Context Summary", expanded=False):
            for key, value in st.session_state.business_context.items():
                if value and key != 'goals':
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                elif key == 'goals' and value:
                    st.write(f"**Goals:** {', '.join(value)}")

    st.info("Every business is unique. Rather than generic data packages, we intelligently choose data variables strategically optimized for your specific business and brand objectives.")
    
    if st.button("Generate Enrichment Recommendations", type="primary"):
        with st.spinner("Analyzing your business context..."):
            try:                
                selected_vars = select_variables_with_ai(st.session_state.business_context)
                st.session_state.selected_variables = selected_vars
                
                # Log successful variable selection
                st.session_state.logger.log_event("ai_variable_selection", {
                    "variables_selected": len(selected_vars),
                    "categories": list(set([var.get('category', 'unknown') for var in selected_vars])),
                    "business_industry": st.session_state.business_context.get('industry', 'Unknown'),
                    "ai_success": True,
                    "schema_integrated": True
                })
                
                st.success("✅ Here are the selected variables optimized for your business!")
                show_ai_variable_explanations(selected_vars)
                
            except Exception as e:
                st.error(f"AI selection failed: {str(e)}")
                
                # Log AI failure and fallback usage
                st.session_state.logger.log_event("ai_variable_selection", {
                    "ai_success": False,
                    "error_type": type(e).__name__,
                    "fallback_used": True,
                    "variables_selected": 3
                })
                
                st.info("Using fallback variable selection...")
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
    """Display AI-selected variables with their strategic rationale in professional table format"""
    st.subheader("Recommended Variables & Strategic Rationale")
    
    if not variables:
        st.warning("No variables were selected.")
        return
    
    # Create markdown table
    table_header = "| Variable | Category | Strategic Rationale |\n|----------|----------|--------------------|\n"
    table_rows = ""
    
    for var in variables:
        variable_name = var.get('variable', 'Unknown')
        category = var.get('category', 'other').title()
        rationale = var.get('rationale', 'No rationale provided')
        
        # Clean up rationale for table display
        rationale = rationale.replace('|', '&#124;').replace('\n', ' ')
        
        table_rows += f"| **{variable_name}** | {category} | {rationale} |\n"
    
    # Display the markdown table
    st.markdown(table_header + table_rows)
    
    # Add summary stats
    col1, col2, col3 = st.columns(3)
    
    # Count by category
    category_counts = {}
    for var in variables:
        cat = var.get('category', 'other').title()
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    with col1:
        st.metric("Total Variables", len(variables))
    
    with col2:
        if category_counts:
            top_category = max(category_counts.items(), key=lambda x: x[1])
            st.metric("Primary Focus", f"{top_category[0]} ({top_category[1]})")
    
    with col3:
        st.metric("Categories", len(category_counts))
    
    # Optional: Show category breakdown in expander
    with st.expander("📊 View Category Breakdown"):
        for category, count in sorted(category_counts.items()):
            st.write(f"**{category}:** {count} variable{'s' if count != 1 else ''}")
            cat_vars = [var['variable'] for var in variables if var.get('category', '').title() == category]
            st.caption(", ".join(cat_vars))

def show_data_enrichment():
    st.header("⚡ Step 4: Data Enrichment")
    st.markdown("Connecting to identity graph and enriching your customer data...")
    
    # Show selected variables in table format
    if st.session_state.selected_variables:
        st.subheader("🎯 Selected Variables for Enrichment")
        
        # Create markdown table using the same format as Step 3
        table_header = "| Variable | Category | Strategic Rationale |\n|----------|----------|--------------------|\n"
        table_rows = ""
        
        for var in st.session_state.selected_variables:
            variable_name = var.get('variable', 'Unknown')
            category = var.get('category', 'other').title()
            rationale = var.get('rationale', 'No rationale provided')
            
            rationale = rationale.replace('|', '&#124;').replace('\n', ' ')
            table_rows += f"| **{variable_name}** | {category} | {rationale} |\n"
        
        st.markdown(table_header + table_rows)
        st.caption(f"Ready to enrich {len(st.session_state.client_data):,} customer records with {len(st.session_state.selected_variables)} strategic variables")
    
    if st.button("🚀 Start Data Enrichment", type="primary"):
        with st.spinner("Enriching data via Brand Response graph..."):
            import time
            time.sleep(2)
            
            try:
                # Load the real enriched data
                data_path = "data/sample_enriched_data.csv"
                if os.path.exists(data_path):
                    enriched_df = pd.read_csv(data_path)
                    st.session_state.enriched_data = enriched_df
                    match_rate = min(len(enriched_df), len(st.session_state.client_data)) / len(st.session_state.client_data)
                    
                    # Log successful enrichment
                    st.session_state.logger.log_event("data_enrichment_complete", {
                        "records_processed": len(st.session_state.client_data),
                        "variables_added": len(st.session_state.selected_variables),
                        "match_rate_percent": f"{match_rate:.1%}",
                        "enrichment_source": "identity_graph_simulation"
                    })
                    
                    st.success("✅ Enterprise-level data enrichment completed in under 2 minutes!")
                    
                    # Show enrichment results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Records Processed", f"{len(st.session_state.client_data):,}")
                    with col2:
                        st.metric("Variables Added", f"{len(st.session_state.selected_variables)}")
                    with col3:
                        st.metric("Match Rate", f"{match_rate:.1%}")
                    
                    # Show sample of enriched data
                    st.subheader("📊 Enriched Data Preview")
                    st.markdown("Your customer data has been enhanced with strategic variables from our data sources:")
                    
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
                    
                    st.session_state.logger.log_event("data_enrichment_complete", {
                        "records_processed": len(st.session_state.client_data),
                        "variables_added": len(st.session_state.selected_variables),
                        "match_rate_percent": "87.3%",
                        "enrichment_source": "mock_data_fallback"
                    })
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Records Processed", f"{len(st.session_state.client_data):,}")
                    with col2:
                        st.metric("Variables Added", f"{len(st.session_state.selected_variables)}")
                    with col3:
                        st.metric("Match Rate", "87.3%")
                
            except Exception as e:
                st.error(f"Enrichment failed: {str(e)}")
                st.session_state.logger.log_event("data_enrichment_error", {
                    "error": str(e),
                    "error_type": type(e).__name__
                })
    
    # Show continue button if data exists
    if st.session_state.enriched_data is not None:
        st.markdown("---")
        if st.button("Continue to Insights Generation →", type="primary", key="continue_to_insights"):
            st.session_state.step = 5
            st.rerun()

def show_generate_insights():
    st.header("📈 Step 5: Generate Strategic Insights")
    
    # Check if we have the required data
    if st.session_state.enriched_data is None or not st.session_state.selected_variables:
        st.warning("Please complete previous steps first.")
        return
    
    st.markdown("Analyzing your customer data to generate actionable brand strategy insights...")
    
    # Generate insights button
    if st.button("Generate Customer Intelligence Report", type="primary"):
        with st.spinner("AI is analyzing your customer data and generating strategic insights..."):
            try:
                insights = generate_customer_insights(
                    st.session_state.enriched_data, 
                    st.session_state.business_context,
                    st.session_state.selected_variables
                )
                
                st.session_state.insights = insights
                
                # Log successful insights generation
                st.session_state.logger.log_event("insights_generated", {
                    "records_analyzed": insights.get('records_analyzed', 0),
                    "variables_analyzed": insights.get('variables_analyzed', 0),
                    "ai_analysis_success": True,
                    "business_industry": st.session_state.business_context.get('industry', 'Unknown')
                })
                
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
                
                # Log insights generation failure
                st.session_state.logger.log_event("insights_generated", {
                    "ai_analysis_success": False,
                    "error": str(e),
                    "fallback_used": True
                })
                
                # Fallback insights for demo
                st.session_state.insights = {
                    'insights_text': "**Demo Insights**: Your customer base shows interesting patterns that differ from typical assumptions. Consider adjusting your brand positioning based on the enriched data analysis.",
                    'variables_analyzed': len(st.session_state.selected_variables),
                    'records_analyzed': len(st.session_state.enriched_data) if isinstance(st.session_state.enriched_data, pd.DataFrame) else 500
                }
    
    # Display insights if available
    if st.session_state.insights and 'insights_text' in st.session_state.insights:
        st.success(f"✅ {len(st.session_state.client_data)} customer records converted to strategic brand insights in minutes!")
        
        # Show analysis summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Records Analyzed", st.session_state.insights.get('records_analyzed', 0))
        with col2:
            st.metric("Variables Analyzed", st.session_state.insights.get('variables_analyzed', 0))
        with col3:
            st.metric("Report Status", "Complete ✓")
        
        st.markdown("---")
        
        # Display the insights in a professional format
        insights_container = st.container()
        with insights_container:
            # Add custom CSS for professional report styling
            st.markdown("""
            <style>
            .insights-report {
                background: white;
                padding: 2rem;
                border-radius: 8px;
                border: 1px solid #e1e5e9;
                margin: 1rem 0;
            }
            .insights-report h1 {
                color: #1f2937;
                border-bottom: 2px solid #4f46e5;
                padding-bottom: 0.5rem;
            }
            .insights-report h2 {
                color: #374151;
                margin-top: 1.5rem;
            }
            .insights-report table {
                margin: 1rem 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display the insights with proper markdown rendering
            st.markdown('<div class="insights-report">', unsafe_allow_html=True)
            st.markdown(st.session_state.insights['insights_text'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add Brand Response branding
            st.markdown("---")
            st.markdown("**Brand Response** | Customer Intelligence Analysis")
            st.caption(f"Report generated from {st.session_state.insights.get('records_analyzed', 0)} customer records using {st.session_state.insights.get('variables_analyzed', 0)} strategic variables")
        
        # Continue button
        if st.button("Continue to Export Report →", type="primary"):
            st.session_state.step = 6
            st.rerun()

def show_report_export():
    st.header("📄 Step 6: Export Customer Intelligence Report")
    st.markdown("Your customer intelligence analysis is complete!")
    
    if st.session_state.insights and 'insights_text' in st.session_state.insights:
        # Show analysis summary metrics first
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Records Analyzed", st.session_state.insights.get('records_analyzed', 0))
        with col2:
            st.metric("Variables Analyzed", st.session_state.insights.get('variables_analyzed', 0))
        with col3:
            st.metric("Report Status", "Complete ✓")
        
        st.markdown("---")
        
        # Add professional styling
        st.markdown("""
        <style>
        .insights-report {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            border: 1px solid #e1e5e9;
            margin: 1rem 0;
        }
        .insights-report h1 {
            color: #1f2937;
            border-bottom: 2px solid #4f46e5;
            padding-bottom: 0.5rem;
        }
        .insights-report h2 {
            color: #374151;
            margin-top: 1.5rem;
        }
        .insights-report table {
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display the actual insights
        st.markdown('<div class="insights-report">', unsafe_allow_html=True)
        st.markdown(st.session_state.insights['insights_text'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add Brand Response branding
        st.markdown("---")
        st.markdown("**Brand Response** | Customer Intelligence Analysis")
        st.caption(f"Report generated from {st.session_state.insights.get('records_analyzed', 0)} customer records using {st.session_state.insights.get('variables_analyzed', 0)} strategic variables")
        
        # Export Options
        st.markdown("---")
        st.subheader("📥 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create text summary for download
            report_text = generate_text_report()
            if st.download_button(
                label="📄 Download Text Report",
                data=report_text,
                file_name=f"{st.session_state.business_context.get('business_name', 'Customer')}_Intelligence_Report.txt",
                mime="text/plain"
            ):
                st.session_state.logger.log_event("report_exported", {
                    "format": "text",
                    "business_name": st.session_state.business_context.get('business_name', 'Unknown')
                })
        
        with col2:
            # JSON export for further analysis
            import json
            report_data = {
                'business_context': st.session_state.business_context,
                'selected_variables': st.session_state.selected_variables,
                'insights': st.session_state.insights,
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if st.download_button(
                label="📊 Download JSON Data",
                data=json.dumps(report_data, indent=2),
                file_name=f"{st.session_state.business_context.get('business_name', 'Customer')}_Analysis_Data.json",
                mime="application/json"
            ):
                st.session_state.logger.log_event("report_exported", {
                    "format": "json",
                    "business_name": st.session_state.business_context.get('business_name', 'Unknown')
                })
        
        # Workflow Summary Section
        if st.session_state.get('logger'):
            st.markdown("---")
            st.subheader("Platform Workflow Analysis")
            st.markdown("Generate summary of this session:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Internal Analysis", help="Summary for internal team - technical capabilities focus"):
                    with st.spinner("Generating internal workflow summary..."):
                        summary = st.session_state.logger.generate_workflow_summary("internal")
                        st.markdown("**Internal Platform Summary:**")
                        st.markdown(summary)
                        
                        st.session_state.logger.log_event("workflow_summary_generated", {
                            "audience": "internal",
                            "summary_length": len(summary)
                        })
            
            with col2:
                if st.button("👔 Client Summary", help="Summary for customer presentation - value focus"):
                    with st.spinner("Generating client summary..."):
                        summary = st.session_state.logger.generate_workflow_summary("customer")
                        st.markdown("**Client Presentation Summary:**")
                        st.markdown(summary)
                        
                        st.session_state.logger.log_event("workflow_summary_generated", {
                            "audience": "customer",
                            "summary_length": len(summary)
                        })
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Start New Analysis", type="secondary"):
                # Log session completion before reset
                st.session_state.logger.log_event("session_completed", {
                    "completion_type": "new_analysis_started",
                    "total_records": st.session_state.insights.get('records_analyzed', 0),
                    "business_industry": st.session_state.business_context.get('industry', 'Unknown')
                })
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("🎯 Refine Analysis", type="secondary"):
                st.session_state.logger.log_event("analysis_refinement", {
                    "refinement_type": "variable_reselection"
                })
                st.session_state.step = 3  # Go back to variable selection
                st.rerun()
    
    else:
        st.warning("No insights available. Please complete the analysis first.")
        if st.button("← Back to Generate Insights"):
            st.session_state.step = 5
            st.rerun()

def generate_text_report():
    """Generate a formatted text report from actual insights data"""
    business_name = st.session_state.business_context.get('business_name', 'Your Business')
    insights = st.session_state.insights
    
    # Get the actual insights text (which is already formatted)
    insights_text = insights.get('insights_text', 'No insights available')
    
    # Convert markdown to plain text for the text report
    import re
    plain_text = re.sub(r'[#*_`]', '', insights_text)  # Remove markdown formatting
    plain_text = re.sub(r'\|[^|]*\|', '', plain_text)  # Remove table formatting
    plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)  # Clean up spacing
    
    report = f"""CUSTOMER INTELLIGENCE REPORT
{business_name}
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

{plain_text}

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

if __name__ == "__main__":
    main()