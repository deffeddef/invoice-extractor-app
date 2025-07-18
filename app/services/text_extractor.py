import pdfplumber
import tesserocr
from PIL import Image
import io

def extract_text_from_txt(file_stream):
    """Extracts text from a .txt file stream."""
    return file_stream.read().decode('utf-8')

def extract_text_from_pdf(file_stream):
    """
    Extracts text from a PDF file stream.
    Tries to extract text directly. If it fails or extracts minimal text,
    it falls back to OCR.
    """
    text = ""
    try:
        with pdfplumber.open(file_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If direct extraction yields little text, try OCR as a fallback
        if len(text.strip()) < 100: # Threshold to trigger OCR
            print("Direct text extraction yielded minimal results. Falling back to OCR.")
            file_stream.seek(0) # Reset stream for OCR
            text = ocr_pdf(file_stream)

    except Exception as e:
        print(f"Error with direct PDF text extraction: {e}. Falling back to OCR.")
        file_stream.seek(0) # Reset stream for OCR
        text = ocr_pdf(file_stream)
        
    return text

def ocr_pdf(file_stream):
    """
    Performs OCR on each page of a PDF file stream.
    """
    text = ""
    try:
        with pdfplumber.open(file_stream) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"Performing OCR on page {i+1}...")
                # Convert page to image
                img = page.to_image(resolution=300).original
                
                # Use tesserocr to perform OCR on the image
                text += tesserocr.image_to_text(img) + "\n"
    except Exception as e:
        print(f"An error occurred during OCR: {e}")
        return "OCR processing failed."
        
    return text

def extract_text(file_name: str, file_stream: io.BytesIO):
    """
    Extracts text from a file based on its extension.
    """
    if file_name.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_stream)
    elif file_name.lower().endswith('.txt'):
        return extract_text_from_txt(file_stream)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")

