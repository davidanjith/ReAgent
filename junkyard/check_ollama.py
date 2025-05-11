import requests
import json
import subprocess
import sys
import os

def run_ollama_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return None, str(e)

def check_ollama_status():
    print("\n🔍 Checking Ollama Status...")
    
    # Check if Ollama process is running
    if sys.platform == "win32":
        check_cmd = ["tasklist", "/FI", "IMAGENAME eq ollama.exe"]
    else:
        check_cmd = ["ps", "aux", "|", "grep", "ollama"]
    
    stdout, stderr = run_ollama_command(check_cmd)
    if "ollama" in stdout:
        print("✅ Ollama process is running")
    else:
        print("❌ Ollama process is not running")
        print("Please start Ollama and try again")
        return False

    # Check Ollama API
    try:
        response = requests.get('http://localhost:11434/api/tags')
        print(f"\nAPI Response Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Ollama API is responding")
            models = response.json()
            print("\nAvailable models:")
            for model in models.get('models', []):
                print(f"- {model['name']} (Size: {model.get('size', 'N/A')})")
            
            if any(model['name'] == 'llama2' for model in models.get('models', [])):
                print("\n✅ llama2 model is found")
                return True
            else:
                print("\n❌ llama2 model is not found")
                print("\nTrying to pull llama2 model...")
                stdout, stderr = run_ollama_command(["ollama", "pull", "llama2"])
                if stdout:
                    print("Output:", stdout)
                if stderr:
                    print("Error:", stderr)
                return False
        else:
            print(f"❌ Unexpected API response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama API")
        print("Please make sure Ollama is running on port 11434")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {str(e)}")
        return False

def main():
    print("🔍 Starting Ollama Diagnostic...")
    
    # Check Ollama installation
    stdout, stderr = run_ollama_command(["ollama", "--version"])
    if stdout:
        print(f"✅ Ollama version: {stdout}")
    else:
        print("❌ Ollama command not found")
        print("Please make sure Ollama is installed correctly")
        return

    # Check Ollama status and models
    if check_ollama_status():
        print("\n✨ Ollama setup looks good!")
    else:
        print("\n❌ Ollama setup needs attention")
        print("\nTroubleshooting steps:")
        print("1. Make sure Ollama is running")
        print("2. Try pulling the model again: ollama pull llama2")
        print("3. Check if you have enough disk space")
        print("4. Check Ollama logs for any errors")

if __name__ == "__main__":
    main() 