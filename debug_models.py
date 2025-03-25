"""
Helper script to view available Gemini models and test basic functionality
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

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
    
    # List available models
    print("Available Gemini models:")
    models = genai.list_models()
    
    # Print models that support content generation
    print("\nModels that support generateContent:")
    generate_models = [model for model in models if "generateContent" in model.supported_generation_methods]
    for model in generate_models:
        print(f"- {model.name}")
    
    # Test a simple summarization with the first available model
    if generate_models:
        try:
            test_model = genai.GenerativeModel(generate_models[0].name)
            test_response = test_model.generate_content("Hello, could you summarize the benefits of using FastAPI?")
            print("\nTest response from model:")
            print(test_response.text)
            print("\nAPI is working correctly!")
        except Exception as e:
            print(f"\nError testing API: {str(e)}")
    else:
        print("\nNo models available that support content generation.")

if __name__ == "__main__":
    main()
