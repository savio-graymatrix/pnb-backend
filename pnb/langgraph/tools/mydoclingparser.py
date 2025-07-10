from pathlib import Path
from typing import List, Any, Dict
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions, TableFormerMode, TableStructureOptions, smolvlm_picture_description
from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption, PowerpointFormatOption
#from base import DocumentParser
import logging
_log = logging.getLogger(__name__)

image_prompt = """Your task is to extract data and insights from any embedded images, charts or diagrams in the PDF.Please do the following:
1. Analyze any **charts or diagrams** in the document (even those that may be image-based but appear in OCR text).
2. If the image contains fields such as names, addresses, PAN, aadhar, etc. extract it very accurately.
3. If the image contains any loan related information, extract it in **structured** format with appropriate keys and values.
4. If the image contains **tabular data**, extract it in **structured** format with appropriate keys and values.
5. If the image is a **chart or diagram**, summarize it by describing:
- What the chart shows
- Axis labels, units, values, trends, and comparisons
6. If specific numerical values are visible, extract it very accurately.
7. Keep the explanation complete.
**IMPORTANT**: Since your extracted content is going to be used for loan analysis, make sure you extract the data properly and accurately.
"""



class DoclingParser():
    """Parser implementation using Docling."""
    def __init__(self):
        self.easyocr_options = EasyOcrOptions(lang=["hi", "en"])
        self.table_structure_options = TableStructureOptions(mode=TableFormerMode.ACCURATE)
        self.picture_description_options = smolvlm_picture_description
        smolvlm_picture_description.prompt = image_prompt
        
        self.pipeline_options = PdfPipelineOptions(
            do_ocr=True,
            force_full_page_ocr=True,
            ocr_options=self.easyocr_options,
            do_table_structure=True,
            table_structure_options=self.table_structure_options,
            do_picture_description=True,
            picture_description_options=self.picture_description_options
        )
        self.converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=self.pipeline_options)        }
    )
    
    def parse(self, page_nos: List[int], doc: Any) -> Dict[str, Any]:
        """Parse the document using Docling.
        Args:
            page_nos (List[int]): List of page numbers to parse.
            doc (Any): Document object or path to parse.
        Returns:
            Dict[str, Any]: Parsed content with metadata.
        Raises:
            ValueError: If page_nos or doc is invalid.
            RuntimeError: If parsing fails.
        """
        page_range = tuple(page_nos)
        if not page_range or not all(isinstance(n, int) and n >= 0 for n in page_range):
            raise ValueError("Docling : Invalid page numbers provided.")
        if not doc:
            raise ValueError("Docling : Document object is required.")
        try:
            _log.info("Docling - Started Document Parsing")
            input_doc = Path(doc) if isinstance(doc, str) else doc
            filename = input_doc.name
            
            _log.info("Docling : Input Document Path", input_doc,"   Page Range", page_range)
            converted_doc = self.converter.convert(input_doc).document

            _log.info("Docling - Exporting Document to Text Format")
            text_content = converted_doc.export_to_text()          

            _log.info("Docling - Completed Document Parsing")
            return {
                "parser": "docling",
                "input_format": input_doc.suffix,
                "filename": filename,
                "content": text_content,
                "page_nos": page_range,
                "status": "success"
            }
        except Exception as e:
            _log.error(f"Docling : Parsing failed: {str(e)}")
            raise RuntimeError(f"Docling : Parsing failed: {str(e)}")

#page_range only takes two inputs: start_page and end_page. (input should be a tuple)
# It will not work, if the your requirement is for multiple pages. It only works for start page to end page.

if __name__ == "__main__":
    doc = r"C:\Users\USER\Downloads\ASHIRWAD POLYCLINIC\CO KYC\ID CARD.pdf"
    page_nos = (1)
    parser = DoclingParser()
    result = parser.parse(page_nos, doc)
    print(result)
    with open("docling_output_2_Kamanwala-14-15_poorscan.txt", "w", encoding="utf-8") as f:
        f.write(result["content"])
