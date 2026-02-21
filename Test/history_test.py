import os
from collections import deque
from groq import Groq

class FastContextManager:
    def __init__(self, max_words=10000):
        # deque allows O(1) popping from the left when we exceed limits
        self.messages = deque()
        self.current_word_count = 0
        self.max_words = max_words
        
        # Initialize Groq client (expects GROQ_API_KEY in environment)
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def _count_words(self, text: str) -> int:
        """A highly optimized, rudimentary word counter."""
        return len(text.split())

    def add_message(self, role: str, content: str):
        """Adds a new message and strictly prunes old context to stay under limit."""
        word_count = self._count_words(content)
        
        # Add the new message to the active memory
        self.messages.append({"role": role, "content": content, "words": word_count})
        self.current_word_count += word_count

        # Instantaneous pruning: drop oldest messages until under the word limit
        while self.current_word_count > self.max_words and len(self.messages) > 1:
            # Pop the oldest message (index 0)
            oldest_msg = self.messages.popleft()
            self.current_word_count -= oldest_msg["words"]

    def generate_response(self, user_prompt: str) -> str:
        """Sends the active context to Groq and returns the response."""
        self.add_message("user", user_prompt)

        # Groq API requires a standard list of dictionaries without our custom 'words' key
        api_payload = [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]

        # Network call: This is the only bottleneck
        chat_completion = self.client.chat.completions.create(
            messages=api_payload,
            model="llama-3.3-70b-versatile", # Or your preferred Groq model
        )

        response_text = chat_completion.choices[0].message.content
        self.add_message("assistant", response_text)
        
        return response_text

# --- Usage Example ---
if __name__ == "__main__":
    # Ensure your API key is set: os.environ["GROQ_API_KEY"] = "your_key"
    chat = FastContextManager(max_words=10000)
    
    reply = chat.generate_response("Hello, let's start a long conversation.")
    print("Groq:", reply)