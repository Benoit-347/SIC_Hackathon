import textwrap
from deep_translator import GoogleTranslator

def translate_massive_text(raw_text, target_language='en', chunk_limit=4000):
    """
    Translates large texts by breaking them into safe chunks to avoid API server limits.
    """
    print(f"\n[SYSTEM] Preparing to translate {len(raw_text)} characters...")
    
    # Initialize the translator
    translator = GoogleTranslator(source='auto', target=target_language)
    
    # textwrap breaks the string safely at word boundaries so we don't slice a word in half
    # replace_whitespace=False ensures we keep the original paragraphs and line breaks
    text_chunks = textwrap.wrap(raw_text, width=chunk_limit, replace_whitespace=False)
    
    print(f"[SYSTEM] Text partitioned into {len(text_chunks)} chunks for processing.")
    
    translated_full_text = ""
    
    # Process each chunk sequentially
    for i, chunk in enumerate(text_chunks):
        try:
            print(f"  -> Translating chunk {i + 1}/{len(text_chunks)}...")
            # Translate and append to our master string
            translated_chunk = translator.translate(chunk)
            translated_full_text += translated_chunk + " "
            
        except Exception as e:
            print(f"\n[ERROR] Failed to translate chunk {i + 1}. Error: {e}")
            # If a chunk fails, we append a warning but keep the program running
            translated_full_text += f"\n[TRANSLATION ERROR IN THIS SECTION]\n"
            
    return translated_full_text.strip()

# ==========================================
# EXECUTION TEST
# ==========================================
if __name__ == "__main__":
    # Simulating a massive Spanish text input
    # In your actual script, this would be your `data = file_1.read()` variable
    
    with open("temp.txt", encoding='utf-8') as file_1:
        massive_spanish_text = str(file_1.readlines())
        
    english_result = translate_massive_text(massive_spanish_text)
    
    print("\n--- TRANSLATION COMPLETE ---")
    # Print the first 500 characters to verify success
    print(english_result)
    