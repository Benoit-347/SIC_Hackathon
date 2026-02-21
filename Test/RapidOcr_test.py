from rapidocr_pdf import RapidOCRPDF
import time

start_time = time.time()
pdf_extracter = RapidOCRPDF()
pdf_path = "SIC_Chapter_7.pdf"

# Extracts text directly from the PDF (returns a list)
texts = pdf_extracter(pdf_path)

# JOIN the list into a single string separated by newlines
final_text = "\n".join([str(t) for t in texts])

with open("OCROutput.txt", 'w', encoding='utf-8') as file_2:
    file_2.write(final_text)
    
end_time = time.time()

print(f"RUNTIME: {end_time - start_time} seconds")