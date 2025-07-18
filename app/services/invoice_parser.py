import io
from app.services.text_extractor import extract_text
from app.services.llm_service import get_llm_service
from app.services.sustainability_service import get_sustainability_service
from app.models.invoice import Invoice, ExtractionResult
from pydantic import ValidationError

def parse_invoice(file_name: str, file_stream: io.BytesIO) -> ExtractionResult:
    """
    Orchestrates the invoice parsing process.
    1. Extracts text from the document.
    2. Uses the LLM to extract structured data.
    3. Validates the data against the Pydantic model.
    4. Enriches data with sustainability metrics.
    """
    try:
        llm_service = get_llm_service()
        sustainability_service = get_sustainability_service()

        # 1. Extract text from the document
        print("Step 1: Extracting text from the document...")
        text = extract_text(file_name, file_stream)
        if not text or text.strip() == "":
            print("Error: Text extraction failed or returned empty.")
            return ExtractionResult(status="error", error_message="Failed to extract text from the document.")
        print("Text extracted successfully.")

        # 2. Use LLM to extract structured data
        print("Step 2: Extracting structured data using LLM...")
        extracted_data = llm_service.extract_invoice_data(text)
        if "error" in extracted_data:
            print(f"Error: LLM extraction returned an error: {extracted_data['error']}")
            return ExtractionResult(status="error", error_message=extracted_data["error"])
        print("LLM extraction complete.")

        # 3. Validate the data with Pydantic
        print("Step 3: Validating extracted data...")
        try:
            invoice = Invoice(**extracted_data)
            print("Validation successful.")
        except ValidationError as e:
            print(f"Error: Pydantic validation failed: {e}")
            return ExtractionResult(
                status="error",
                error_message=f"Validation failed. The LLM returned data that does not match the required schema. Details: {e}"
            )

        # 4. Enrich data with sustainability metrics
        print("Step 4: Enriching data with sustainability metrics...")
        invoice = sustainability_service.analyze_invoice_sustainability(invoice)
        print("Sustainability analysis complete.")

        return ExtractionResult(status="success", invoice_data=invoice)

    except ValueError as e:
        print(f"Error: ValueError in parsing pipeline: {e}")
        return ExtractionResult(status="error", error_message=str(e))
    except Exception as e:
        print(f"Error: An unexpected error occurred in the parsing pipeline: {e}")
        return ExtractionResult(status="error", error_message="An unexpected error occurred.")
