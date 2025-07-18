import pytest
import io
from app.services.text_extractor import extract_text

def test_extract_text_from_txt_file():
    file_content = b"This is a test text file."
    file_stream = io.BytesIO(file_content)
    text = extract_text("test.txt", file_stream)
    assert text == "This is a test text file."

def test_extract_text_from_pdf_file_placeholder():
    # For a real PDF test, you would need a sample PDF file.
    # Here, we'll simulate an empty PDF or a PDF that Tesseract can't process well.
    # In a real scenario, you'd have a small, known PDF for testing.
    file_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000074 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF"
    file_stream = io.BytesIO(file_content)
    text = extract_text("empty.pdf", file_stream)
    # Expect empty string or very minimal output for an empty/malformed PDF
    assert isinstance(text, str)
    # We can't assert specific content without a real PDF and Tesseract setup
    # For now, just ensure it doesn't crash and returns a string.

def test_extract_text_unsupported_file_type():
    file_content = b"some image data"
    file_stream = io.BytesIO(file_content)
    text = extract_text("image.jpg", file_stream)
    assert text == ""
