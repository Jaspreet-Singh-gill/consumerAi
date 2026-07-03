import os
import uuid
from langchain_community.document_loaders import PyPDFLoader

def extract_text_from_pdf(pdf_bytes: bytes) -> tuple[str, str]:
    """
    Extracts text from PDF bytes using PyPDFLoader.
    Cleans up the temporary file immediately after reading.
    Returns:
        (extracted_text, status) where status is "processed" or "scanned_unreadable"
    """
    if not pdf_bytes:
        return "", "none"

    # Create a temporary file name
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")

    try:
        # Write bytes to temporary file
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)

        # Load using PyPDFLoader
        loader = PyPDFLoader(temp_path)
        pages = loader.load()
        
        # Combine text from all pages
        full_text = "\n".join([page.page_content for page in pages]).strip()

        # Check if the document appears to be scanned/unreadable
        # If total characters extracted is extremely low (e.g., < 100 characters), it's likely scanned
        if len(full_text) < 100:
            return "", "scanned_unreadable"

        return full_text, "processed"

    except Exception as e:
        print(f"Error extracting PDF: {str(e)}")
        return "", "scanned_unreadable"

    finally:
        # Guarantee cleanup
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Failed to delete temp file {temp_path}: {e}")
