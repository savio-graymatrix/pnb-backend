from langchain.tools import tool
import os
import pymupdf4llm
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from typing import List

@tool
def extract_from_file(file_url: str):
    """Extracts content from files"""
    file, ext = os.path.splitext(file_url)
    file_path = f"{os.getcwd()}/logs/files/{file_url}"

    def fallback_ocr(path: str):
        print("Falling back to OCR...")
        pages = convert_from_path(path, dpi=300)
        texts = [pytesseract.image_to_string(img) for img in pages]
        return texts

    def structured_pdf_parser(path: str):
        try:
            chunks = pymupdf4llm.to_markdown(path, page_chunks=True)
            texts = [c["text"] for c in chunks if c.get("text", "").strip()]
            if texts:
                return texts
        except Exception as e:
            print(f"Structured parser failed: {e}")
            return None

    match (ext):
        case ".pdf":
            return structured_pdf_parser(file_path) or fallback_ocr(file_path)
        case _:
            try:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
                return text.strip()
            except Exception as e:
                return f"OCR failed: {e}"

print(extract_from_file("C:\\Users\\USER\\Downloads\\DhiyaVentures.pdf"))