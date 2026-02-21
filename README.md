Features:
1. Uses groq llama 3.3 70B versatile model, to infer text.
2. Provides method to convert any language to English via deep-translator.
	Has 500 word limit, Solution- Translate in chunks, then merge all words into 1 string
3. Provides user with option to input text file for conversion.
4. Provides pdf upload option as well. > uses EasyOcr and To convert Non selectable text/ images to text.
	If pdf text is too long, sends text as chunks to groq.
5. Maintains chat history of user. If the conversation is too big, uses sliding window to delete old history.
	Uses collections module in py for history (1D array of string, with O(1) operations on history.

Setup:
go to: https://console.groq.com/home
create your api key

RUN:
	pip install requirements.txt
	$env:GROQ_API_KEY= "Your_api_key"		;At powershell
	pyton -m streamlit run ./test.py
