import os
from typing import List, Any, Dict
from pathlib import Path
from dotenv import load_dotenv
from llama_cloud_services.parse import LlamaParse


class LlamaParser():
    """Parser implementation using LlamaParse."""
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not self.api_key:
            raise RuntimeError("LLAMA_CLOUD_API_KEY is not set.")
        self.parser = LlamaParse(
            api_key=self.api_key,
            result_type="markdown",
            premium_mode=True,
            show_progress=True,
            target_pages=""  # Will be set in parse method
        )
    
    def parse(self, page_nos: Any, doc: Any) -> Dict[str, Any]:
        """Parse the document using LlamaParse.
        Args:
            page_nos (Any): Comma-separated string of page numbers or 'all' for all pages.
            doc (Any): Document object or path to parse.
        Returns:
            Dict[str, Any]: Parsed content with metadata and image descriptions.
        Raises:
            ValueError: If page_nos or doc is invalid.
            RuntimeError: If parsing fails.
        """
        input_doc = Path(doc) if isinstance(doc, str) else doc
        filename = input_doc.name.strip(".pdf")
        if not doc:
            raise ValueError("Document object is required.")
        target_pages = page_nos if page_nos != "all" else ""
        if page_nos != "all":
            try:
                target_pages = page_nos
            except ValueError as e:
                raise ValueError(f"Invalid page numbers format: {str(e)}")        
        try:
            print("LlamaParse : Started Document Parsing")
            self.parser.target_pages = target_pages
            result_job = self.parser.parse(doc)
            text_documents = result_job.get_text_documents(split_by_page=False)
            txt = text_documents
            print("LlamaParse : Completed Document Parsing")
            return {
                "parser": "llama",
                "filename": filename,
                "input_format": input_doc.suffix,
                "content": txt,
                "page_nos": page_nos,
                "status": "success"
            }
        except Exception as e:
            raise RuntimeError(f"LlamaParse : Parsing failed: {str(e)}")




# if __name__ == "__main__":
#     doc = r"C:\Users\USER\Downloads\2_Kamanwala-14-15_poorscan.pdf"
#     page_nos = "all"
#     parser = LlamaParser()
#     result = parser.parse(page_nos, doc)
#     ans = result.text
#     print(ans)
#     with open("llama_output_2_Kamanwala-14-15_poorscan.txt", "w", encoding="utf-8") as f:
#         f.write(ans)
