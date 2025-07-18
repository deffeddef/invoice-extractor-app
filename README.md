# Invoice Extractor AI

A scalable service to accept PDF/TXT invoices, extract relevant fields using a local LLM, and return structured JSON output.

## Features

- **HTTP API**: Endpoint to upload PDF or TXT invoices.
- **Automated Model Download**: Downloads the required LLM model on first startup.
- **Local LLM**: Uses a local LLaMA-based model (Mistral 7B) for inference.
- **OCR Fallback**: Employs Tesseract for PDFs where text extraction is difficult.
- **Structured Output**: Defines a clear JSON schema for extracted data using Pydantic, now including VAT IDs, detailed line-items (quantity, tax, discount, sustainability score), and full payment-terms (net-days, early-pay discount, late-fee).
- **Sustainability Engine**: Queries external ratings (EcoVadis, B-Corp, EU Ecolabel, CO₂ APIs - currently simulated) and flags green vendors, CO₂-intensive items, packaging waste, and overall ESG risk.
- **Configurable**: Uses a `.env` file for easy configuration of model and sustainability API details.
- **Containerized**: Comes with a `Dockerfile` for easy deployment.

## Project Structure
```
invoice_extractor_app/
├── app/
│   ├── api/
│   │   └── endpoints.py
│   ├── models/
│   │   └── invoice.py
│   ├── services/
│   │   ├── invoice_parser.py
│   │   ├── llm_service.py
│   │   ├── sustainability_service.py # New: For sustainability analysis
│   │   └── text_extractor.py
│   ├── utils/
│   │   └── helpers.py
│   ├── config.py             # Configuration loader
│   └── main.py               # Main FastAPI application
├── model/
│   └── .gitkeep
├── .env                      # Environment variables
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

## Setup and Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd invoice_extractor_app
```

### 2. Create a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages. This includes `python-dotenv` for managing configuration.
```bash
pip install -r requirements.txt
```

You also need to install Google's Tesseract OCR engine on your system.
- **On macOS (using Homebrew):**
  ```bash
  brew install tesseract
  ```
- **On Debian/Ubuntu:**
  ```bash
  sudo apt-get update
  sudo apt-get install tesseract-ocr libtesseract-dev
  ```

### 4. Configure the Application
The application is configured using a `.env` file. A default `.env` file is included with the project. You can modify it to change the model or other settings.

**Key settings in `.env`:**
- `MODEL_URL`: The URL to download the GGUF model from.
- `MODEL_DIR`: The local directory to store the model.
- `MODEL_NAME`: The filename for the downloaded model.
- `ECOVADIS_API_KEY`: (Optional) API key for EcoVadis integration.
- `B_CORP_API_URL`: (Optional) URL for B-Corp API.
- `EU_ECOLABEL_API_URL`: (Optional) URL for EU Ecolabel API.
- `CO2_API_URL`: (Optional) URL for CO2 emissions API.

## How to Run the Application

Once the setup is complete, you can run the application using Uvicorn. Make sure you are inside the `invoice_extractor_app` directory.

```bash
uvicorn app.main:app --reload
```

On the first run, the application will automatically download the LLM model specified in your `.env` file. This might take some time depending on your internet connection. The model will be saved in the `model/` directory. Subsequent startups will be much faster.

The API will be available at `http://127.0.0.1:8000`.

## Running Tests

To run the automated tests, navigate to the `invoice_extractor_app` directory and execute `pytest`:

```bash
pytest
```

This will discover and run all tests in the `tests/` directory.

## API Usage

You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

### Upload Invoice
- **Endpoint**: `POST /api/upload`
- **Description**: Upload a PDF or TXT file to extract invoice data.
- **Request**: `multipart/form-data` with a `file` field containing the invoice.

#### Example using `curl`:
```bash
curl -X POST "http://127.0.0.1:8000/api/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/invoice.pdf"
```


## Running with Docker

To build and run the application using Docker:

1.  **Build the Docker image:**
    ```bash
    docker build -t invoice-extractor .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 invoice-extractor
    ```

The first time you run the container, it will download the LLM model inside the container. This is a one-time setup process. The API will become available once the download is complete.

