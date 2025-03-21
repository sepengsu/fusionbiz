import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_response(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """
    Generate a response from OpenAI API based on the provided prompt
    
    Args:
        prompt (str): The prompt to send to the API
        model (str): The model to use for generation
        temperature (float): Controls randomness in the output
        
    Returns:
        str: The generated response
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def prompt_engineering_example():
    # Examples of prompt engineering techniques
    
    # Basic prompt
    basic_prompt = "What is prompt engineering?"
    print("Basic prompt result:")
    print(generate_response(basic_prompt))
    print("-" * 50)
    
    # Few-shot learning
    few_shot_prompt = """
    Convert these sentences to French:
    English: Hello, how are you?
    French: Bonjour, comment allez-vous?
    
    English: I would like to order food.
    French: Je voudrais commander de la nourriture.
    
    English: Where is the nearest train station?
    French:
    """
    print("Few-shot learning result:")
    print(generate_response(few_shot_prompt))
    print("-" * 50)
    
    # Chain of thought
    cot_prompt = """
    Solve this step by step:
    If a shirt costs $25 and is discounted by 20%, then a customer uses a $5 coupon, what is the final price?
    """
    print("Chain of thought result:")
    print(generate_response(cot_prompt))
    print("-" * 50)
    
    # Role prompting
    role_prompt = """
    Act as an expert in cybersecurity. What are the top 5 security practices for a small business?
    """
    print("Role prompting result:")
    print(generate_response(role_prompt))

if __name__ == "__main__":
    # Before running this code, create a .env file with your API key:
    # OPENAI_API_KEY=your_api_key_here
    
    # Test the API connection
    response = generate_response("Hello, how are you today?")
    print("API Test Response:")
    print(response)
    print("\n" + "=" * 50 + "\n")
    
    # Run prompt engineering examples
    prompt_engineering_example()