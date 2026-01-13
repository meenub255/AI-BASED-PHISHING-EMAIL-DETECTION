import ollama
import traceback

print("Testing Ollama Connection...")
try:
    # Try to list models to check connection
    models = ollama.list()
    print("Success! Connected to Ollama.")
    # Debug print
    import pprint
    pprint.pprint(models)
    
    # Check if llama3 is present
    model_names = [m.get('name') or m.get('model') for m in models.get('models', [])]
    print(f"Available models: {model_names}")

    if any('llama3' in m for m in model_names):
        print("Llama 3 is available!")
    else:
        print("WARNING: llama3 not found. You may need to run 'ollama pull llama3'")
        
except Exception as e:
    print("Connection Failed!")
    traceback.print_exc()
