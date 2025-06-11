import requests
import json
from typing import Optional

class SmartDeepSeek:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        
        self.free_model = "deepseek/deepseek-r1-0528-qwen3-8b:free"
        self.paid_model = "deepseek/deepseek-chat"  
        self.reason_model = "deepseek/deepseek-reason" 
        
        self.base_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-educational-app.com",  
            "X-Title": "Educational Chatbot"  # Change this
        }
        
        self.complexity_threshold = 15  # Word count
        self.dissatisfaction_triggers = [
            "not satisfied", "explain better", 
            "more detail", "incomplete answer"
        ]

    def needs_paid_model(self, question: str, previous_response: str = "") -> bool:
        """Determine if question requires paid model"""
        question_lower = question.lower()
        
        if any(trigger in previous_response.lower() 
               for trigger in self.dissatisfaction_triggers):
            return True
            
        if len(question.split()) > self.complexity_threshold:
            return True
            
        technical_terms = [
            "explain in detail", "step-by-step", 
            "prove that", "compare and contrast"
        ]
        if any(term in question_lower for term in technical_terms):
            return True
            
        return False

    def query_model(self, model: str, question: str) -> Optional[str]:
        """Generic model query with optimized prompts"""
        prompts = {
            self.free_model: f"Provide a helpful response to: {question}",
            self.paid_model: f"""As an expert, analyze this in depth:
{question}
Include examples and practical applications""",
            self.reason_model: f"""Perform rigorous step-by-step analysis:
1. Problem: {question}
2. Key components
3. Logical relationships
4. Final synthesized answer"""
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompts[model]
                }
            ],
            "temperature": 0.5
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.base_headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()  
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"API Error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response content: {e.response.text}")
            return None

    def get_response(self, question: str, previous_response: str = "") -> str:
        """Smart response generator"""
        if self.needs_paid_model(question, previous_response):
            response = self.query_model(self.paid_model, question)
            if not response:
                response = self.query_model(self.reason_model, question)
        else:
            response = self.query_model(self.free_model, question)
            
        return response or "I couldn't generate a response for this question."

# Example usage
if __name__ == "__main__":
    # Initialize with your OpenRouter API key
    assistant = SmartDeepSeek("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")

    # # First interaction (simple question)
    # q1 = "What is photosynthesis?"
    # response = assistant.get_response(q1)
    # print(f"Q: {q1}\nA: {response}\n")

    # # Follow-up showing dissatisfaction
    # q2 = "I need more detail about the light-dependent reactions"
    # response = assistant.get_response(q2, previous_response=response)
    # print(f"Q: {q2}\nA: {response}\n")

    # Complex question
    q3 = "who is cm of telangana"
    response = assistant.get_response(q3)
    print(f"Q: {q3}\nA: {response}")
    