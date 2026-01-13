import os
import json
import ollama
from typing import Dict, Any, List
from src.state import AgentReport
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name: str, model_name: str = "llama3"):
        self.name = name
        self.model_name = model_name
        # Using Ollama client implicitly via library
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Define the persona and rules for this specific agent."""
        pass
    
    def _build_prompt(self, state: Dict[str, Any]) -> str:
        """Construct the prompt from the current state."""
        # Simple default implementation
        return f"EMAIL SUBJECT: {state.get('subject')}\nEMAIL BODY: {state.get('body_text')}"

    def analyze(self, state: Dict[str, Any]) -> AgentReport:
        """Standard method to perform analysis using local Ollama model."""
        print(f"[{self.name}] Starting local analysis (Model: {self.model_name})...")
        
        prompt = self._build_prompt(state)
        
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
            
            # Ollama returns a dict with 'message' -> 'content'
            content = response['message']['content']
            result = json.loads(content)
            
            return AgentReport(
                agent_name=self.name,
                verdict=result.get("verdict", "UNKNOWN"),
                confidence_score=result.get("confidence_score", 0.0),
                reasoning=result.get("reasoning", []),
                metadata=result.get("metadata", {})
            )
        except Exception as e:
            print(f"[{self.name}] Error during local analysis: {e}")
            return AgentReport(
                agent_name=self.name,
                verdict="ERROR",
                confidence_score=0.0,
                reasoning=[f"Agent error: {str(e)}"],
                metadata={"error": str(e)}
            )
