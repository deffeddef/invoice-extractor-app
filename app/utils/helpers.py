
import os
import requests
from tqdm import tqdm

def download_model(url, destination_folder, file_name):
    """
    Downloads a file from a URL to a destination folder with a progress bar.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    file_path = os.path.join(destination_folder, file_name)

    if os.path.exists(file_path):
        print(f"Model already exists at {file_path}. Skipping download.")
        return file_path

    try:
        print(f"Downloading model from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(file_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong during download.")
            # Clean up partially downloaded file
            os.remove(file_path)
            return None

        print(f"Model downloaded successfully to {file_path}")
        return file_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading model: {e}")
        if os.path.exists(file_path):
            os.remove(file_path) # Clean up
        return None

if __name__ == "__main__":
    # Example usage: Download a small LLaMA-based model
    # Using a small, capable model like Mistral 7B Instruct v0.2 GGUF
    MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    MODEL_DIR = "model"
    MODEL_NAME = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    
    download_model(MODEL_URL, MODEL_DIR, MODEL_NAME)
