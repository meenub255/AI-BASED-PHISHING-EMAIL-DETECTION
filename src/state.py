from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class AgentReport(BaseModel):
    agent_name: str
    verdict: str  # e.g., "SUSPICIOUS", "SAFE", "PHISHING"
    confidence_score: float  # 0.0 to 100.0
    reasoning: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class PhishState(BaseModel):
    # Input Data
    email_id: str
    subject: str
    sender: str
    raw_headers: str
    body_text: str
    body_html: Optional[str] = None
    
    # Internal State & Analysis
    screenshot_path: Optional[str] = None
    reports: List[AgentReport] = Field(default_factory=list)
    
    # Final Verdict (set by Judge Agent)
    risk_score: float = 0.0  # 0 to 100
    is_phishing: bool = False
    final_summary: str = ""
    status: str = "PENDING"  # PENDING, ANALYZING, FINISHED, ERROR
