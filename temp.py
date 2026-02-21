import os
import sys
import time
import textwrap
from collections import deque
from deep_translator import GoogleTranslator
from rapidocr_pdf import RapidOCRPDF
from groq import Groq

# --- TRANSLATOR ---
def translate_massive_text(raw_text, target_language='en', chunk_limit=4000):
    print(f"\n[SYSTEM] Preparing to translate {len(raw_text)} characters...")
    translator = GoogleTranslator(source='auto', target=target_language)
    text_chunks = textwrap.wrap(raw_text, width=chunk_limit, replace_whitespace=False)
    
    print(f"[SYSTEM] Text partitioned into {len(text_chunks)} chunks for processing.\nStarting Translation!\n")
    translation_start_time = time.time()
    translated_full_text = ""
    
    for i, chunk in enumerate(text_chunks):
        try:
            print(f"  -> Translating chunk {i + 1}/{len(text_chunks)}...")
            translated_chunk = translator.translate(chunk)
            translated_full_text += translated_chunk + " "
        except Exception as e:
            print(f"\n[ERROR] Failed to translate chunk {i + 1}. Error: {e}")
            translated_full_text += f"\n[TRANSLATION ERROR IN THIS SECTION]\n"
            
    translation_end_time = time.time()
    print(f"Translation took {translation_end_time - translation_start_time:.2f} seconds")
    return translated_full_text.strip()

# --- SUMMARIZER ---
def summarize_in_chunks(raw_text, client):
    print(f"\n[SYSTEM] Preparing to summarize text...")
    
    # 40,000 chars is roughly 9,500 tokens. 
    text_chunks = textwrap.wrap(raw_text, width=40000, replace_whitespace=False)
    print(f"[SYSTEM] Text partitioned into {len(text_chunks)} chunks for summarization.")
    
    system_prompt = """
    You are an expert content synthesizer.
    Summarize the provided text.
    Focus on factual accuracy and eliminate fluff.
    Style: Use concise paragraphs. Use ASCII art or bullet points to structure.
    Do NOT be redundant.
    """
    
    full_summary = ""
    
    for i, chunk in enumerate(text_chunks):
        print(f"\n -> Sending Chunk {i + 1}/{len(text_chunks)} to Groq...")
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk}
                ]
            )
            chunk_summary = completion.choices[0].message.content
            full_summary += f"\n\n--- Summary of Part {i + 1} ---\n" + chunk_summary
            
            # CRITICAL WARNING: If you are on the free tier, waiting only 3 seconds 
            # after sending ~9,500 tokens WILL trigger a 413 error on chunk 2. 
            # You must wait roughly 60 seconds for the TPM bucket to empty.
            if i < len(text_chunks) - 1:
                print(" -> Waiting 1 second (Groq's TPM rate limit)...")
                time.sleep(1) 
                
        except Exception as e:
            print(f"[ERROR] Groq API failed on chunk {i + 1}: {e}")
            
    return full_summary

# --- CONTEXT MANAGER (HISTORY) ---
class FastContextManager:
    def __init__(self, max_words=10000):
        self.messages = deque()
        self.current_word_count = 0
        self.max_words = max_words
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def _count_words(self, text: str) -> int:
        return len(text.split())

    def add_message(self, role: str, content: str):
        word_count = self._count_words(content)
        self.messages.append({"role": role, "content": content, "words": word_count})
        self.current_word_count += word_count

        while self.current_word_count > self.max_words and len(self.messages) > 1:
            oldest_msg = self.messages.popleft()
            self.current_word_count -= oldest_msg["words"]

    def generate_response(self, user_prompt: str) -> str:
        self.add_message("user", user_prompt)
        api_payload = [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]

        chat_completion = self.client.chat.completions.create(
            messages=api_payload,
            model="llama-3.3-70b-versatile", 
        )

        response_text = chat_completion.choices[0].message.content
        self.add_message("assistant", response_text)
        return response_text

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    file_read_start_time = time.time()
    data = ""

    user_input = input("Do you want to upload pdf/txt/paste text?: (2/1/0) ")

    if user_input == '2':
        pdf_extracter = RapidOCRPDF()
        pdf_path = input("Enter pdf path: ") 
        text_per_pages = pdf_extracter(pdf_path)
        num_pages = len(text_per_pages)
        print(f"Total pages detected: {num_pages}")
        
        # [REMOVED THE 20-PAGE LIMIT HERE]
        # It will now process all pages in the PDF.
            
        data = "\n".join([str(t[1]) if isinstance(t, tuple) else str(t) for t in text_per_pages])
        
    elif user_input == '1':
        file_name = input("Enter file name: ")
        with open(file_name, encoding='utf-8') as file_1:
            data = file_1.read()
            
    elif user_input == '0':
        data = input("\nEnter the text you want to summarize: ")
        
    else:
        print("Invalid input!")
        sys.exit()

    file_read_end_time = time.time()
    print(f"Data ingestion took: {file_read_end_time - file_read_start_time:.2f} seconds")

    eng_user_input = input("\nDo you want to convert output to english?: (1 for Yes, 0 for No) ")
    if eng_user_input == "1":
        data = translate_massive_text(data)

    print("\nStarting AI text summarization!")
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) 
    
    api_request_start_time = time.time()
    final_output = summarize_in_chunks(data, groq_client)
    api_request_end_time = time.time()

    print("\n" + "="*50)
    print("FINAL SUMMARY:")
    print("="*50)
    print(final_output)
    print(f"\nGroq API total time: {api_request_end_time - api_request_start_time:.2f} seconds")

    # ==========================================================
    # PHASE 2: INTERACTIVE CHAT WITH MEMORY
    # ==========================================================
    print("\n" + "="*50)
    print("INITIALIZING CHAT MEMORY WITH DOCUMENT...")
    print("="*50)
    
    # 1. Initialize the Context Manager
    chat = FastContextManager(max_words=10000)
    
    # 2. Inject the summary directly into the memory as context
    system_instruction = f"You are a helpful assistant. Base your answers on this document summary:\n{final_output}"
    chat.add_message("system", system_instruction)
    
    print("Memory initialized! You can now ask questions about the document.")
    print("Type 'quit' or 'exit' to stop.")
    
    # 3. Start the infinite chat loop
    while True:
        prompt = input("\nYou: ")
        if prompt.lower() in ['quit', 'exit']:
            print("Ending session. Good luck with the Hackathon!")
            break
            
        print("\nGroq is typing...")
        reply = chat.generate_response(prompt)
        print(f"\nGroq: {reply}")