import easyocr
import os
import sys

def run_local_ocr(image_path, languages=['es', 'en']):
    """
    Executes local Optical Character Recognition on a target image.
    Loads models into memory only when called.
    """
    print(f"[SYSTEM] Initializing Neural Network for languages: {languages}...")
    
    try:
        # Initialize the Reader. 
        # Set gpu=True if you have a dedicated GPU with CUDA configured. 
        # Setting gpu=False forces the CPU to handle the matrix math.
        reader = easyocr.Reader(languages, gpu=False)
        
        print(f"[SYSTEM] Scanning image array: {image_path}...\n")
        
        # readtext() processes the image. 
        # detail=1 returns the full data structure (Boxes, Text, Confidence).
        # paragraph=False keeps the line-by-line breakdown intact.
        raw_results = reader.readtext(image_path, detail=1, paragraph=False)
        
        full_extracted_text = ""
        
        print("--- LOW-LEVEL ENGINE OUTPUT ---")
        # Parse the nested data structure returned by the model
        for item in raw_results:
            bounding_box = item[0]
            detected_text = item[1]
            confidence_score = item[2]
            
            # Print the matrix breakdown for debugging and verification
            print(f"Text: {detected_text:<30} | Confidence: {confidence_score:.4f}")
            
            full_extracted_text += detected_text + " "
            
        return full_extracted_text.strip()

    except Exception as e:
        print(f"\n[FATAL ERROR] OCR Engine failed: {e}")
        sys.exit(1)

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    # Replace this with the path to your actual image file
    target_image = "sample_spanish_document.jpg"
    
    if not os.path.exists(target_image):
        print(f"[SYSTEM ERROR] File '{target_image}' not found in the current directory.")
        print("Please place an image in the folder and update the filename.")
    else:
        final_text = run_local_ocr(target_image)
        
        print("\n==========================================")
        print("FINAL EXTRACTED STRING")
        print("==========================================")
        print(final_text)