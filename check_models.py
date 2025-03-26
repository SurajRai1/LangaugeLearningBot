import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def list_available_models():
    """List all available models for the provided API key"""
    try:
        models = openai.models.list()
        print("Available models:")
        for model in models.data:
            print(f"- {model.id}")
        
        print("\nRecommended models for chat applications:")
        for model in models.data:
            if "gpt" in model.id and ("turbo" in model.id or "gpt-4" in model.id):
                print(f"- {model.id}")
                
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    list_available_models() 