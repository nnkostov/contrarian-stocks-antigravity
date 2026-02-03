import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def check_environment():
    print("--- Environment Diagnostic ---")
    
    # 1. Check for .env file
    env_path = ".env"
    if os.path.exists(env_path):
        print(f"[OK] Found .env file at {os.path.abspath(env_path)}")
        load_dotenv()
    else:
        print(f"[FAIL] No .env file found at {os.path.abspath(env_path)}")
        return

    # 2. Check for API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        print(f"[OK] GEMINI_API_KEY found: {masked_key}")
    else:
        print("[FAIL] GEMINI_API_KEY not found in environment.")
        return

    # 3. Test Gemini API
    print("\n--- Testing Gemini API Connection ---")
    # 3. Test Gemini API & List Models
    print("\n--- Listing Available Models ---")
    try:
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Found model: {m.name}")
        
        print("\n--- Testing Generation with 'gemini-3-pro-preview' ---")
        model = genai.GenerativeModel('gemini-3-pro-preview')
        response = model.generate_content("Say 'Hello from Gemini 3 Pro!'")
        print(f"[SUCCESS] AI Response: {response.text}")

    except Exception as e:
        print(f"[FAIL] Error during generation: {e}")

if __name__ == "__main__":
    check_environment()
