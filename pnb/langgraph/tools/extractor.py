from os.path import splitext
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib
from keybert import KeyBERT
from pnb.db.data_models import ExtractedDocument, File, ExtractedDocumentMetadata
from langchain.tools import tool
import os
import pymupdf4llm
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from langchain_core.documents import Document
from pnb import SETTINGS
import requests
import tempfile

kw_model = KeyBERT()


async def store_text_embedding(parent_document_id: str, file_url: str) -> None:
    """
    Store Text Embeddings for the file to the Vector Storage

    :params:
    file_name (str): Document Name in Static Storage

    :returns:
    None

    :raises:
    FileTypeNotSupported
    """
    # Step 1: Load file
    file_path = file_url
    file_type = splitext(file_url)[-1]
    documents = None
    if file_type == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
    elif file_type in [".pdf", ".jpeg", ".jfif", ".jpg"]:
        documents = [
            Document(page_content=i.encode("utf-8"))
            for i in extract_from_file(file_path)
        ]

    # Step 2: Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    # Step 3: Add metadata (e.g. file name, hash)
    file_hash = hashlib.sha256(
        "".join([x.page_content for x in documents]).encode("utf-8")
    ).hexdigest()
    extracted_documents = list()
    for i, doc in enumerate(chunks):
        extracted_document_obj = ExtractedDocument(
            name=file_url,
            content=doc.page_content,
            link_to=parent_document_id,
            metadata=ExtractedDocumentMetadata(
                filename=file_url,
                filetype=file_type,
                chunk_index=i,
                hash=file_hash,
                tags=[
                    t[0] for t in kw_model.extract_keywords(doc.page_content, top_n=5)
                ],
            ),
        )
        extracted_documents.append(extracted_document_obj)
    await ExtractedDocument.insert_many(extracted_documents)

pytesseract.pytesseract.tesseract_cmd = SETTINGS.TESSERACT_PATH

@tool
def extract_from_file(file_url: str):
    """Extracts content from files"""
    file, ext = os.path.splitext(file_url)
    file_path = (
        f"{os.getcwd()}/logs/files/{file_url}"
        if not file_url.startswith("http")
        else file_url
    )

    def fallback_ocr(path: str):
        print("Falling back to OCR...")

        if path.startswith("http"):
            response = requests.get(path)
            response.raise_for_status()  # fail if URL is invalid

            # Step 2: Save to temp file
            tmp_path = None
            texts = None
            
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            pages = convert_from_path(tmp_path, dpi=300, poppler_path=SETTINGS.POPPLER_PATH)
            texts = [pytesseract.image_to_string(img) for img in pages]
            os.remove(tmp_path)
            return texts
        pages = convert_from_path(path, dpi=300, poppler_path=SETTINGS.POPPLER_PATH)
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
