import ollama
import sys

print("Attempting to pull 'llama3.2:1b' model...")

try:
    # This acts as a generator for progress
    current_digest = ''
    for progress in ollama.pull('llama3.2:1b', stream=True):
        digest = progress.get('digest', '')
        if digest != current_digest and digest:
             print(f"\nPulling layer: {digest[0:12]}...")
             current_digest = digest
        
        if 'completed' in progress and 'total' in progress:
             percent = int((progress['completed'] / progress['total']) * 100)
             sys.stdout.write(f"\r{progress.get('status')}: {percent}%")
             sys.stdout.flush()
    
    print("\n\nSuccess! 'llama3' is ready.")
    
except Exception as e:
    print(f"\nError pulling model: {e}")
