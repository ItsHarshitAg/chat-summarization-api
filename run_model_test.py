"""
Test script to find which Gemini model works with your API key
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_model(model_name):
    """Test if a specific model works"""
    try:
        print(f"Testing model: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, what are the benefits of using MongoDB?")
        
        if hasattr(response, 'text'):
            print(f"✅ SUCCESS - Model {model_name} works!")
            print(f"Response: {response.text[:100]}...\n")
            return True
        else:
            print(f"❌ FAILED - Model {model_name} didn't return expected format\n")
            return False
    except Exception as e:
        print(f"❌ FAILED - Model {model_name}: {str(e)}\n")
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("Error: Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
        return
    
    # Configure the Gemini API
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Get available models
    print("Fetching available models...")
    try:
        models = genai.list_models()
        content_models = [model.name for model in models if "generateContent" in model.supported_generation_methods]
        print(f"Found {len(content_models)} models that support content generation:\n")
        for model in content_models:
            print(f"- {model}")
        print("\n")
    except Exception as e:
        print(f"Error listing models: {str(e)}")
        content_models = []
    
    # Models to test (both with and without "models/" prefix)
    model_names = [
        # Standard names
        "gemini-pro",
        "gemini-1.0-pro",
        # Full paths
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-pro",
    ]
    
    # Add available models to our list
    for model in content_models:
        if model not in model_names:
            model_names.append(model)
    
    # Test each model
    print("Testing models one by one:")
    working_models = []
    
    for model_name in model_names:
        if test_model(model_name):
            working_models.append(model_name)
    
    # Summary
    if working_models:
        print(f"SUMMARY: Working models for your API key:")
        for model in working_models:
            print(f"- {model}")
        print(f"\nRECOMMENDATION: Use '{working_models[0]}' in your main.py file")
    else:
        print("No working models found. Please check your API key and permissions.")

if __name__ == "__main__":
    main()
