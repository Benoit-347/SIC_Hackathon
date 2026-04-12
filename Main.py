import time
from deep_translator import GoogleTranslator
import textwrap
from rapidocr_pdf import RapidOCRPDF
from groq import Groq
import os, sys, time

def read_pdf_to_text(pdf_path):
    
    # initialze PDF- OCR + extractor    object.     (pdf contains selectable (word embedd) or images)
    pdf_OCR_Extractor = RapidOCRPDF()   # along with above, runs on ONNX runtime- (lightweight mathematical framework) package to run speed ai models. (Recognize letter symbols from pixels fast)
                                            # much faster than tesseract, the above line loads the OCR model into memory.
    # obtain text from conversion.
    text_pages = pdf_OCR_Extractor(pdf_path)
    
    num_pages = len(text_pages)
    print(f"Extracted {num_pages} pages from pdf.")
    return text_pages


def translate(text):
    """
    Uses Online GoogleTranlate, by mimic'ing a user typing it.
    Google's translate TPU's translate as fast as 1000 words in ms.
    Google network is optimized to do translation due to optimized Endpoints.
    """
    
     # Initialize the translator: create object, loaded with url to scrape the Internet for GoogleTranslation, mimic'ing a browser
    Translator_obj = GoogleTranslator(source='auto', target='en')    # detect language of source text- automatic    ; target languange- english
    
    # String splitter- textwrapper: to divide string at word boundaries at certain word count.
    text_chunks = textwrap.wrap(text, width=3000, replace_whitespace=False)     # width is the count after which split happens, replacing strips at word boundaries.
    print(f"\nPartitioned text into: {len(text_chunks)} chunks")
    
    output_text = ""
    
    i, num_chunks = 1, len(text_chunks)
    for chunk in text_chunks:
        try:
            print(f"Translating chunk {i}/{num_chunks}")
            output_text += Translator_obj.translate(chunk)
        except Exception as e:
            print(f"Failed to translate chunk: {i} \nError: {e} \nText: {chunk} \nContinuing loop!")
            output_text += "THIS SECTION WAS SKIPPED DUE TO ERROR IN TRANSLATION"
        i += 1
    
    return output_text.strip()

    
def send_guess_engine_prompt(prompt, model_name):
    try:
        # creates a http client, to be able to send and recieve requests over internet via Groq() object. (our internet connection)
        client = Groq(api_key= os.getenv("GROQ_API_KEY"))

    except:
        print('Set your groq api key at env. \nThe command for powershell is: #env: GROQ_API_KEY = "your_api_key"')
        sys.exit()
    # next step: sending the request from client to Groq() API via internet (http)
        # client.chat -> route my request to department of model conversation. (Else client would have to prepare for .mp3..etc)
        # client.chat.completion -> AI's just perform math on ur input to return its response ur output. A response to your patter.
            # So chat.completion is the category of task, i.e. response to uesr_prompt.
    completion = client.chat.completions    # via create() fn converts our dict to json, posts to https of groq/model
    instructions = "Consider yourself a very technical and factual, genuine Researcher. Do not be too redundant."
    completion = completion.create(model= model_name, messages=[
        {"role": "system",
         "content": instructions},
        {"role": "user",
         "content": prompt}
        ]
    )
    input_tokens = completion.usage.prompt_tokens
    guess_tokens = completion.usage.completion_tokens
    end_via = completion.choices[0].finish_reason
    # 1 line of py code = 10 tokens.
    print(f"\nYour prompt took: \t{input_tokens} tokens, \nguessing took: \t\t{guess_tokens} tokens, \nEnd via: \t\t{end_via}\n")
    return completion.choices[0].message.content


def main(): 
    
    text = input("ENTer: ")
    
    translation_start_time = time.time()
    Eng_text = translate(text)
    translation_end_time = time.time()    
    
    model_name = 'llama-3.3-70b-versatile'  # qwen/qwen3-32b    'llama-3.3-70b-versatile'
    print("Enter your text,     end: press ctrl+z, + enter (windows):- ", end='')
    Input_pattern = sys.stdin.read()
    prompt_start_time = time.time()
    response = send_guess_engine_prompt(Input_pattern, model_name)
    print(f"Response was: {response}")
    prompt_end_time = time.time()
    
    print(f"\nThe response from model-{model_name} is: \n{response}")    
    print(f"\nANALYTICS: \nTranslation time: {translation_end_time - translation_start_time} \nGroq prompt response time: {prompt_end_time - prompt_start_time}")
    

# translator:  keep count, instead of counting each time for split (FAster count). Use better data structure instead of dict to store data.
# after creating chunks, try doing batch requests for translation and gess_engine_api. (parallel execution)
# string_var += i   ; over a loop is O(N^2) scaling, as the size of original stirng also contributes to creation of new string.


def test_pdf_reader(pdf_path):
    print(f"The output of pdf reader: {read_pdf_to_text(pdf_path)}")
def test_translate(text):
    output_text = translate(text)
    print(f"Translated text is: {output_text}")
def test_send_guess_engine_prompt(model_name):
    prompt = """In the following code, where could be apply the concepts of Data Structures and Design techniques of algorithms, to perform faster code execution.
    Give example with using Inline C++ code with python."""
    with open("geminni_merged_main.py", encoding='UTF-8') as file_1:
        prompt += file_1.read()
    print(f"\n\nThe response starts here:\n {send_guess_engine_prompt(prompt, model_name)}")
    
def test():
    
    #with open("./temp/spanish_text.txt", encoding='UTF-8') as file_1:
    #    text = file_1.read()
    #test_translate(text)
    
    #test_pdf_reader(r"C:\Users\benoi\My_Folder\my_repositories\SIC_Hackathon\Test\Java_Module_5.pdf")
    
    # Input_pattern = input("Enter the text, which will be the pattern: ")
    test_send_guess_engine_prompt('qwen/qwen3-32b')
    pass

test()