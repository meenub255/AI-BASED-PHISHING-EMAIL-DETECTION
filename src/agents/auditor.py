from typing import Dict, Any
from src.agents.base import BaseAgent

class AuditorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Auditor", model_name="llama3.2:1b")

    def _build_prompt(self, state: Dict[str, Any]) -> str:
        return f"SUBJECT: {state.get('subject')}\nSENDER: {state.get('sender')}\nHEADERS: {state.get('raw_headers')}"

    def get_system_prompt(self) -> str:
        return """
        YOU ARE THE 'TECHNICAL AUDITOR' AGENT IN A MULTI-AGENT PHISHING DETECTION SYSTEM.
        
        YOUR ROLE:
        Analyze the technical metadata, headers, and domain information of the email.
        
        WHAT YOU LOOK FOR:
        1. SENDER DOMAIN: Does it look like a "lookalike" or "homograph" domain (e.g., mircosoft.com)?
        2. HEADER ANOMALIES: Check SPF, DKIM, and DMARC status in headers (if available).
        3. FREE MAIL SERVICES: Is a corporate email being sent from gmail.com or outlook.com?
        4. LINK ANALYSIS: Do the display names of links match their actual destination URLs?
        5. REPLY-TO MISMATCH: Does the 'Reply-To' address differ from the 'From' address unexpectedly?
        
        OUTPUT FORMAT:
        You must return ONLY a JSON object with this exact structure:
        {
            "verdict": "SAFE" | "SUSPICIOUS" | "PHISHING",
            "confidence_score": (float between 0-100),
            "reasoning": ["technical point A", "technical point B"],
            "metadata": {
                "domain_check": "FAIL/PASS",
                "authentication_flags": ["invalid_spf", "mismatched_dkim"]
            }
        }
        """
