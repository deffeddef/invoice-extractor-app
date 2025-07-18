from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import io

from app.services.invoice_parser import parse_invoice
from app.models.invoice import ExtractionResult

router = APIRouter()

def process_invoice_background(file_name: str, file_content: bytes):
    """
    A wrapper function to run the invoice parsing in the background.
    This function is designed to be called by BackgroundTasks.
    Currently, it just processes and we don't have a mechanism to check the result later.
    For a real-world application, you would save the result to a database
    and provide another endpoint to check the status/result.
    """
    print(f"Background task started for file: {file_name}")
    result = parse_invoice(file_name, io.BytesIO(file_content))
    if result.status == "success":
        print(f"Successfully processed {file_name} in the background.")
        # Here you would typically save result.invoice_data to a database
        # print(result.invoice_data.json(indent=2))
    else:
        print(f"Failed to process {file_name} in the background. Error: {result.error_message}")

@router.post("/upload", response_model=ExtractionResult)
async def upload_invoice(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Accepts an invoice file (PDF or TXT) for processing.
    
    This endpoint demonstrates two approaches:
    1.  **Synchronous:** Processes the invoice immediately and returns the result.
    2.  **Asynchronous (commented out):** Adds the processing task to the background
        and immediately returns a confirmation message.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")

    # Read file content into memory
    file_content = await file.read()
    
    # --- Synchronous Processing ---
    # The parsing is done in the request-response cycle.
    # Good for quick tasks or when the client needs the result immediately.
    result = parse_invoice(file.filename, io.BytesIO(file_content))
    if result.status == "error":
        return JSONResponse(
            status_code=400,
            content={"status": "error", "error_message": result.error_message}
        )
    return result

    # --- Asynchronous Processing (Alternative) ---
    # Uncomment the block below and comment out the synchronous block above
    # to switch to background processing.
    #
    # background_tasks.add_task(process_invoice_background, file.filename, file_content)
    # return JSONResponse(
    #     status_code=202,
    #     content={
    #         "status": "processing_started",
    #         "message": f"Invoice '{file.filename}' has been received and is being processed in the background."
    #     }
    # )

