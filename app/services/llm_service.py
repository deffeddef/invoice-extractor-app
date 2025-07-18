import os
import json
import re
from llama_cpp import Llama
from app.models.invoice import Invoice
from app.config import settings
from functools import lru_cache

# --- Prompt Engineering ---
PROMPT_TEMPLATE = """
You are an expert AI assistant for invoices. Your task is to extract structured data from the provided invoice text.
Ensure you extract the invoice number, invoice date, vendor's full name, address (street, city, **zip code**, country), and VAT ID.
Also, extract the customer's full name and address (street, city, **zip code**, country).
For each line item, extract the description, quantity, unit price, and total.
Crucially, extract the **currency** of the total amount.
Return ONLY the JSON output, matching the following schema exactly. Do NOT include any other text, explanations, or formatting outside the JSON block.

**JSON Schema:**
{schema}

**Invoice Text:**
---
{invoice_text}
---

**Extracted JSON:**
```json
"""


class LLMService:
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            # This check is now a safeguard. The startup event should handle the download.
            raise FileNotFoundError(
                f"Model file not found at {model_path}. "
                "The model should have been downloaded on application startup."
            )
        
        print("Loading LLM model into memory...")
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,  # Offload all layers to GPU if available
            n_ctx=8192,       # Context window
            verbose=False,
            json_mode=True,   # Enable JSON mode
        )
        print("LLM model loaded successfully.")

    def get_invoice_schema(self) -> str:
        """Returns the JSON schema for the Invoice model as a string."""
        return json.dumps(Invoice.model_json_schema(), indent=2)

    def extract_invoice_data(self, text: str) -> dict:
        """
        Extracts invoice data from text using the LLM.
        """
        schema_str = self.get_invoice_schema()
        prompt = PROMPT_TEMPLATE.format(schema=schema_str, invoice_text=text)

        try:
            output = self.llm(
                prompt,
                max_tokens=2048,
                temperature=0.3,
                # Removed stop sequence to prevent premature JSON truncation
                echo=False,
            )
            
            response_text = output['choices'][0]['text'].strip()
            
            # Use regex to find the JSON object
            json_match = re.search(r'```json\n({.*?})\n```', response_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                # Fallback if ```json block is not found, try to find any JSON object
                json_start = response_text.find('{')
                json_end = response_text.rfind('}')
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_string = response_text[json_start : json_end + 1]
                else:
                    raise ValueError("No valid JSON object found in the LLM response.")
            
            return json.loads(json_string)

        except Exception as e:
            print(f"Error during LLM inference or JSON parsing: {e}")
            return {"error": "Failed to extract data from LLM response."}

@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    """
    Factory function to create and cache a singleton instance of the LLMService.
    This ensures the model is only loaded into memory once.
    """
    return LLMService(model_path=settings.model_path)