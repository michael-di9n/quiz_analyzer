import os
import time
import anthropic
from dotenv import load_dotenv

class ClaudeClient:
    """Client for interacting with Claude API"""
    
    def __init__(self, api_key=None):
        """
        Initialize the Claude client
        
        Args:
            api_key (str, optional): Claude API key. If not provided,
                                     will look for ANTHROPIC_API_KEY environment variable
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Claude API key is required. Please provide it or set ANTHROPIC_API_KEY environment variable.")
        
        # Initialize the client
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def ask_question(self, question_text, question_type="multiple_choice", max_tokens=1000, timeout=30):
        """
        Send a question to Claude and get the answer
        
        Args:
            question_text (str): The question text to send
            question_type (str): Either "multiple_choice" or "short_answer"
            max_tokens (int): Maximum tokens in the response
            timeout (int): Timeout in seconds
            
        Returns:
            str: Claude's answer
        """
        # Create appropriate system prompt based on question type
        if question_type == "multiple_choice":
            system_prompt = (
                "You are helping answer a multiple-choice quiz question. "
                "Analyze the question carefully, determine the correct answer choice, "
                "and explain your reasoning. If the answer is clearly one of the provided options, "
                "indicate which option (A, B, C, D, etc.) is correct at the start of your response."
            )
        else:
            system_prompt = (
                "You are helping answer a short-answer quiz question. "
                "Analyze the question carefully and provide a concise but thorough answer. "
                "Make sure to directly address what the question is asking."
            )
        
        # Set up timeout with a timestamp
        start_time = time.time()
        
        try:
            # Create the message
            response = self.client.messages.create(
                model="claude-3-opus-20240229",  # Or other appropriate model
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question_text}
                ]
            )
            
            # Extract the answer text
            answer = response.content[0].text
            return answer
            
        except anthropic.APIError as e:
            return f"API Error: {str(e)}"
        except anthropic.APIConnectionError as e:
            return f"Connection Error: {str(e)}"
        except anthropic.RateLimitError as e:
            return f"Rate Limit Error: {str(e)}"
        except anthropic.APITimeoutError as e:
            return f"Timeout Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
        finally:
            # Log the time it took to get a response
            elapsed_time = time.time() - start_time
            print(f"Claude API call took {elapsed_time:.2f} seconds")
            
            # If we've exceeded the timeout, return an error
            if elapsed_time > timeout:
                return "Request timed out. Claude did not respond within the expected time."