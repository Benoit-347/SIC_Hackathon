from groq import Groq
import os

user_input = input("Do you want to upload file?: ")
if user_input == "1":
    yes = True
else:
    yes = False
    
if (yes):
    print("\nChose upload option!")
    file_name = input("Enter file name: ")
    with open(file_name) as file_1:
        data = str(file_1.readlines())

else:
    data = input("\nEnter the text you want to summarize: ")
    

# Replace 'gsk_...' with your actual key from the Groq Console
client = Groq(api_key= os.getenv("GROQ_API_KEY")) 

completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
                {
            "role": "system",
            "content": """
            You are an expert content synthesizer.
            Summarize the following text using a style.
            Focus on factual accuracy and eliminate fluff.
            Style: Use concise paragraphs
            Do NOT be redundant.
            """
        },
        {
            "role": "user",
            "content": data
        }
    ]
)
print(completion.choices[0].message.content)