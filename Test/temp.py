from groq import Groq
import os
import textwrap
from deep_translator import GoogleTranslator
from rapidocr_pdf import RapidOCRPDF
import time, sys

# TRANSLATOR


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
    
    print(f"[SYSTEM] Text partitioned into {len(text_chunks)} chunks for processing.\nStarting Translation!\n")
    translation_start_time = time.time()
    
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
            
    translation_end_time = time.time()
    print(f"Translation took {translation_end_time - translation_start_time} seconds")
    return translated_full_text.strip()



# User input

# 1. file upload
user_input = input("Do you want to upload pdf/txt/paste text?: (2/1/0) ")

if user_input == '2':
    pdf_read_start_time = time.time()
    pdf_extracter = RapidOCRPDF()
    pdf_path = input("Enter pdf path: ")         #"SIC_Chapter_7.pdf"
    text_per_pages = pdf_extracter(pdf_path)
    num_pages = len(text_per_pages)
    print(num_pages)
    if num_pages < 100:
        print(f"The number of pages in pdf is :{num_pages} \nThis is near limit to send to groq, which is 12k tokens/ 100 pages of pdf!\nConsidering only first 100 pages!")
        text_per_pages = text_per_pages[:50]
    data = "\n".join([str(t) for t in text_per_pages])
    pdf_read_end_time = time.time()
    
elif user_input == '1':
        file_name = input("Enter file name: ")
        with open(file_name, encoding='utf-8') as file_1:
            data = file_1.read()
elif user_input == '0':
    data = input("\nEnter the text you want to summarize: ")
else:
    print("Invalid input!")
    
print(f"Pdf conversion tool: {pdf_read_end_time - pdf_read_start_time} seconds")

# 2. Convert output to english?
eng_user_input = input("\nDo you want to convert output to english?: ")

if eng_user_input == "1":
    print("taking eng route")
    data = translate_massive_text(data)
    print("\nCompleted Translation!")

print("\nStarting AI text summarization!\nSending API request to GROQ!\n")
content = """
            You are an expert content synthesizer.
            You are to summazie text.
            Focus on factual accuracy and eliminate fluff.
            Style: Use concise paragraphs if required But be more structured, may use ASCII art to structure too.
            Do NOT be redundant.
            """

api_request_start_time = time.time()
client = Groq(api_key= os.getenv("GROQ_API_KEY")) 

completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
                {
            "role": "system",
            "content": content
        },
        {
            "role": "user",
            "content": data
        }
    ]
)

output = completion.choices[0].message.content
print(output)


api_request_end_time = time.time()
print(f"groq api request took: {api_request_end_time - api_request_start_time} seconds")

# Extra analytics:
print(f"\nAnalytics: \nNo. of words in input: {len(data)} \t\tNo. of words at summary: {len(output)}")
