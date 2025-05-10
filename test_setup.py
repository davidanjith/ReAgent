import sys
import subprocess
import requests
from pathlib import Path

def check_ollama():
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = response.json()
            if any(model['name'] == 'llama2:latest' for model in models.get('models', [])):
                print("✅ Ollama is running and llama2 model is available")
                return True
            else:
                print("❌ Ollama is running but llama2 model is not found")
                print("Please run: ollama pull llama2")
                return False
        else:
            print("❌ Ollama is not running")
            print("Please start Ollama and try again")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print("Please make sure Ollama is running on port 11434")
        return False

def check_dependencies():
    try:
        import fastapi
        import langchain
        import langchain_core
        import langchain_community
        import arxiv
        print("✅ All Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def main():
    print("🔍 Checking setup...")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install dependencies:")
        print("pip install -r requirements.txt")
        return
    
    # Check Ollama
    if not check_ollama():
        return
    
    print("\n✨ Setup looks good! You can now run the application:")
    print("1. Start the FastAPI server:")
    print("   uvicorn main:app --reload")
    print("\n2. Open ui/index.html in your browser")
    print("\n3. Try searching for a paper and chatting with it!")

if __name__ == "__main__":
    main() 