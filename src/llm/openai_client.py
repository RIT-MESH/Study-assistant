import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

def get_openai_llm():
    """
    Initializes and returns the ChatOpenAI LLM instance.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")
    
    # Initialize the ChatOpenAI model
    llm = ChatOpenAI(
        openai_api_key=api_key,
        model_name="gpt-3.5-turbo", # You can change this to "gpt-4" or other models
        temperature=0.7 # Adjust for more or less creative responses
    )
    
    return llm