# utils/logger.py
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class SessionLogger:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = "logs"
        self.log_file = os.path.join(self.log_dir, f"session_{self.session_id}.log")
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize session
        self.log_event("session_start", {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log an event with timestamp and details"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'details': details
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Logging error: {str(e)}")
    
    def read_session_log(self) -> List[Dict[str, Any]]:
        """Read all events from the current session log"""
        events = []
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            events.append(json.loads(line.strip()))
        except Exception as e:
            print(f"Error reading log: {str(e)}")
        
        return events
    
    def generate_workflow_summary(self, audience: str = "internal") -> str:
        """Generate AI summary of the workflow for specified audience"""
        events = self.read_session_log()
        
        if not events:
            return "No workflow data available."
        
        # Create narrative from events
        workflow_narrative = self._create_workflow_narrative(events)
        
        # Generate AI summary based on audience
        if audience == "internal":
            prompt = f"""You are summarizing a Brand Response Customer Intelligence Platform session for potential partners/users of the platform, such as SMB creative & branding agencies evaluating this technology platform.

        WORKFLOW DATA:
        {workflow_narrative}

        Focus your summary on these key innovations. :
        1. **Contextually Optimized Data Enhancement** - How the platform moves beyond standardized data packages to select variables strategically for this specific business context
        2. **Enterprise-Grade Data at SMB Economics** - Access to sophisticated identity graph data at a fraction of enterprise consulting costs
        3. **Rapid Strategic Transformation** - Converting raw customer data into actionable brand insights in minutes

        Write in factual, journalistic tone emphasizing demonstrated capabilities and competitive advantages. Speak in present tense, not past."""
        
        else:  # customer audience
            prompt = f"""You are summarizing a Brand Response Customer Intelligence analysis for a client who wants to understand what was done and what value they received.

        WORKFLOW DATA:
        {workflow_narrative}

        Create a professional summary that explains:
        1. The analysis that was performed on their customer data
        2. The strategic insights that were generated
        3. The value and actionability of the results
        4. Next steps for implementing the recommendations

        Write in consulting language that demonstrates expertise while being accessible to business owners."""
        
        try:
            response = client.messages.create(
                model=os.getenv("LLM_MODEL", "claude-sonnet-4-20250514"),
                max_tokens=1500,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def _create_workflow_narrative(self, events: List[Dict[str, Any]]) -> str:
        """Create a structured narrative from log events"""
        narrative_parts = []
        
        for event in events:
            event_type = event.get('event', 'unknown')
            details = event.get('details', {})
            timestamp = event.get('timestamp', '')
            
            if event_type == 'data_upload':
                narrative_parts.append(f"Uploaded customer dataset: {details.get('records', 0)} records with {details.get('columns', 0)} data fields")
            
            elif event_type == 'business_context':
                narrative_parts.append(f"Business context captured: {details.get('industry', 'Unknown')} industry, {details.get('business_model', 'Unknown')} model")
            
            elif event_type == 'variable_selection':
                narrative_parts.append(f"AI selected {details.get('variable_count', 0)} strategic variables based on business context")
            
            elif event_type == 'data_enrichment':
                narrative_parts.append(f"Enhanced customer data with {details.get('match_rate', 'N/A')} match rate via identity graph")
            
            elif event_type == 'insights_generation':
                narrative_parts.append(f"Generated strategic insights analyzing {details.get('records_analyzed', 0)} records across {details.get('variables_analyzed', 0)} variables")
            
            elif event_type == 'report_export':
                narrative_parts.append(f"Exported customer intelligence report in {details.get('format', 'unknown')} format")
        
        return "\n".join([f"- {part}" for part in narrative_parts])