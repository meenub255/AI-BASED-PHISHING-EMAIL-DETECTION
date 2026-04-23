from src.agents.base import BaseAgent
from src.state import AgentReport
from typing import List, Dict, Any
import json
import ollama

class JudgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Judge", model_name="llama3.2:1b")

    def get_system_prompt(self) -> str:
        return """
        YOU ARE THE 'FINAL JUDGE' IN A MULTI-AGENT PHISHING DETECTION SYSTEM.
        
        YOUR ROLE:
        Review the reports from the Prosecutor (Social Engineering) and Auditor (Technical Forensics). 
        You must resolve any contradictions and provide the final explainable verdict.
        
        JUDGEMENT RULES:
        - If BOTH find it Phishing, Verdict is PHISHING with 90%+ confidence.
        - If only ONE finds it Phishing, weigh the technical evidence higher.
        - If the Auditor found a lookalike domain, it is almost ALWAYS Phishing.
        - If the Prosecutor found urgency but Auditor found valid DMARC, it might just be a Marketing email (SAFE/SUSPICIOUS).
        
        OUTPUT FORMAT:
        You must return ONLY a JSON object with this exact structure:
        {
            "verdict": "SAFE" | "SUSPICIOUS" | "PHISHING",
            "confidence_score": (float between 0-100),
            "final_summary": "A concise, industry-ready explanation of why this was flagged.",
            "is_phishing": boolean
        }
        """

    def resolve_debate(self, reports: List[AgentReport]) -> Dict[str, Any]:
        """Summarize all previous analysis into a final verdict."""
        print(f"[{self.name}] Synthesizing reports via local LLM...")
        
        reports_summary = "\n---\n".join([
            f"Agent: {r.agent_name}\nVerdict: {r.verdict}\nReasoning: {r.reasoning}"
            for r in reports
        ])
        
        prompt = f"REPORTS TO REVIEW:\n{reports_summary}\n\nProvide the final synthesis in the requested JSON format."
        
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'system',
                    'content': self.get_system_prompt()
                },
                {
                    'role': 'user',
                    'content': prompt
                },
            ], format='json')
            
            content = response['message']['content']
            return json.loads(content)
        except Exception as e:
            print(f"[{self.name}] Error during judgment synthesis: {e}")
            return {
                "verdict": "ERROR",
                "confidence_score": 0.0,
                "final_summary": f"Failed to reach consensus: {str(e)}",
                "is_phishing": False
            }

