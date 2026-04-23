import ollama
import time
import json

MODELS = ["llama3.2:1b", "llama3.2:3b", "phi3", "llama3"]

TEST_EMAIL = """
Subject: Urgent: Unusual login attempt
From: Security Alert <security@micros0ft-support.com>
Body: We detected an unusual login from Russia. If this wasn't you, click here to secure your account immediately: https://fake-link.com/
"""

SYSTEM_PROMPT = "You are a phishing detection expert. Analyze the email and return a JSON with 'verdict' (SAFE/PHISHING) and 'confidence_score' (0-100)."

def benchmark():
    print(f"{'Model':<15} | {'Pull Time':<10} | {'Inference':<10} | {'Verdict':<10}")
    print("-" * 55)

    for model in MODELS:
        # Pull model first
        start_pull = time.time()
        print(f"Pulling {model}...", end="\r")
        ollama.pull(model)
        pull_duration = time.time() - start_pull

        # Measure inference
        start_inf = time.time()
        try:
            response = ollama.chat(model=model, messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': TEST_EMAIL}
            ])
            inf_duration = time.time() - start_inf
            content = response['message']['content']
            verdict = "OK" if "PHISHING" in content.upper() else "SAFE?"
            
            print(f"{model:<15} | {pull_duration:>9.2f}s | {inf_duration:>9.2f}s | {verdict:<10}")
        except Exception as e:
            print(f"{model:<15} | Error: {str(e)}")

if __name__ == "__main__":
    benchmark()
