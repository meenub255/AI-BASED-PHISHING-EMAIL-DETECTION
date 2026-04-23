import os
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from typing import Dict, Any
from src.state import PhishState, AgentReport
from src.agents.prosecutor import ProsecutorAgent
from src.agents.auditor import AuditorAgent
from src.agents.judge import JudgeAgent

load_dotenv()

class PhishGuardOrchestrator:
    def __init__(self):
        self.prosecutor = ProsecutorAgent()
        self.auditor = AuditorAgent()
        self.judge = JudgeAgent()

    def analyze_email(self, email_data: Dict[str, Any]) -> PhishState:
        """The core Custom State Machine logic with parallel execution."""
        start_time = time.time()
        print("\n--- Starting PhishGuard-AI Analysis ---")
        
        # 1. Initialize State
        state = PhishState(
            email_id=email_data.get("id", "MOCK_ID"),
            subject=email_data.get("subject", ""),
            sender=email_data.get("from", ""),
            raw_headers=email_data.get("headers", ""),
            body_text=email_data.get("body_text", ""),
            body_html=email_data.get("body_html", ""),
            status="ANALYZING"
        )

        # 2. Run Analysis Sequentially (Faster on CPU without GPU)
        print("[Orchestrator] Running agents sequentially for CPU efficiency...")
        try:
            # 1. Prosecutor
            state.reports.append(self.prosecutor.analyze(state.model_dump()))
            # 2. Auditor
            state.reports.append(self.auditor.analyze(state.model_dump()))
        except Exception as e:
            print(f"[Orchestrator] Warning: Analysis phase failed: {e}")


        # 3. Final Judgment Phase (Only if at least one report succeeded)
        valid_reports = [r for r in state.reports if r.verdict != "ERROR"]
        
        if valid_reports:
            judgment = self.judge.resolve_debate(valid_reports)
            state.risk_score = judgment.get("confidence_score", 0.0)
            state.is_phishing = judgment.get("is_phishing", False)
            state.final_summary = judgment.get("final_summary", "Synthesis complete.")
        else:
            state.final_summary = "All agents failed due to rate limits or errors. Please try again in 60 seconds."
            state.status = "ERROR"

        state.status = "FINISHED"
        
        duration = time.time() - start_time
        print(f"--- Analysis Complete in {duration:.2f}s: {state.risk_score}% Phishing Risk ---\n")
        return state

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PhishGuard-AI Orchestrator")
    parser.add_argument("--live", action="store_true", help="Enable live streaming from Gmail")
    args = parser.parse_args()

    orchestrator = PhishGuardOrchestrator()

    if args.live:
        from src.utils.gmail import GmailService
        print("--- Starting Gmail Live Stream ---")
        try:
            gmail = GmailService()
            processed_ids = set()
            
            print("Listening for new emails (Ctrl+C to stop)...")
            while True:
                print(".", end="", flush=True) # Polling indicator
                emails = gmail.get_latest_emails(max_results=3)
                for email_data in emails:
                    if email_data['id'] not in processed_ids:
                        print(f"\n[LiveStream] New Email Detected: {email_data['subject']}")
                        final_state = orchestrator.analyze_email(email_data)
                        
                        print(f"VERDICT: {'PHISHING' if final_state.is_phishing else 'SAFE'}")
                        print(f"CONFIDENCE: {final_state.risk_score}%")
                        print(f"REASONING: {final_state.final_summary}")
                        
                        processed_ids.add(email_data['id'])
                
                time.sleep(30) # Poll every 30 seconds
        except Exception as e:
            print(f"Live stream error: {e}")
    else:
        # Mock data for testing
        test_email = {
            "subject": "Urgent: Unusual login attempt on your account",
            "from": "Security Alert <security@micros0ft-support.com>",
            "headers": "Authentication-Results: spf=fail dmarc=none",
            "body_text": "We detected an unusual login from Russia. If this wasn't you, click here to secure your account immediately: https://permitted-restaurants-liquid-whole.trycloudflare.com/ or your account will be suspended."
        }
        
        final_state = orchestrator.analyze_email(test_email)
        
        print(f"VERDICT: {'PHISHING' if final_state.is_phishing else 'SAFE'}")
        print(f"CONFIDENCE: {final_state.risk_score}%")
        print(f"REASONING: {final_state.final_summary}")
