# import os
# import logging
# import PyPDF2
# import pdfplumber
# import fitz  # PyMuPDF
# from typing import Optional, Tuple

# class PDFInputHandler:
#     def __init__(self):
#         self.logger = logging.getLogger(__name__)
#         self.logger.info("PDF handler initialized")

#     def extract_text(self, pdf_path: str) -> Tuple[Optional[str], bool]:
#         """
#         Extract text from PDF using multiple fallback methods
#         Returns: (extracted_text, success_status)
#         """
#         if not os.path.exists(pdf_path):
#             self.logger.error(f"PDF file not found: {pdf_path}")
#             return None, False

#         # Try extraction methods in order of reliability
#         methods = [
#             self._extract_with_pymupdf,
#             self._extract_with_pdfplumber,
#             self._extract_with_pypdf2
#         ]

#         for method in methods:
#             try:
#                 text = method(pdf_path)
#                 if text and len(text.strip()) > 50:  # Minimum viable text
#                     self.logger.info(f"Success with {method.__name__}")
#                     return text, True
#             except Exception as e:
#                 self.logger.warning(f"{method.__name__} failed: {str(e)}")
#                 continue

#         self.logger.error("All PDF extraction methods failed")
#         return None, False

#     def _extract_with_pymupdf(self, pdf_path: str) -> str:
#         """High-quality extraction with PyMuPDF"""
#         text = ""
#         with fitz.open(pdf_path) as doc:
#             for page in doc:
#                 text += page.get_text() + "\n"
#         return text.strip()

#     def _extract_with_pdfplumber(self, pdf_path: str) -> str:
#         """Precise extraction with pdfplumber"""
#         text = ""
#         with pdfplumber.open(pdf_path) as pdf:
#             for page in pdf.pages:
#                 text += page.extract_text() or "" + "\n"
#         return text.strip()

#     def _extract_with_pypdf2(self, pdf_path: str) -> str:
#         """Fallback extraction with PyPDF2"""
#         text = ""
#         with open(pdf_path, 'rb') as file:
#             reader = PyPDF2.PdfReader(file)
#             for page in reader.pages:
#                 text += page.extract_text() or "" + "\n"
#         return text.strip()

#     def get_page_count(self, pdf_path: str) -> int:
#         """Get total page count"""
#         try:
#             with fitz.open(pdf_path) as doc:
#                 return len(doc)
#         except:
#             try:
#                 with pdfplumber.open(pdf_path) as pdf:
#                     return len(pdf.pages)
#             except:
#                 return 0

# # Example usage
# if __name__ == "__main__":
#     import sys
#     logging.basicConfig(level=logging.INFO)
    
#     if len(sys.argv) > 1:
#         pdf_path = sys.argv[1]
#         handler = PDFInputHandler()
#         text, success = handler.extract_text(pdf_path)
        
#         if success:
#             print(f"Extracted {len(text)} characters")
#             print("First 500 chars:\n", text[:500])
#         else:
#             print("Extraction failed")
#     else:
#         print("⚠️  Please provide the path to a PDF file as a command-line argument.")
import os
import sys
import logging
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from docx import Document

logging.basicConfig(level=logging.INFO)

class PDFInputHandler:
    def extract_text(self, pdf_path):
        try:
            with fitz.open(pdf_path) as doc:
                text = "\n".join(page.get_text() for page in doc)
            if len(text.strip()) >= 50:
                logging.info("✅ Extracted text using PyMuPDF.")
                return text.strip(), True
        except Exception as e:
            logging.warning(f"Text-based extraction failed: {e}")

        try:
            logging.info("🔁 Trying OCR...")
            pages = convert_from_path(pdf_path)
            text = ""
            for i, page in enumerate(pages):
                ocr_text = pytesseract.image_to_string(page)
                text += f"\n--- Page {i + 1} ---\n{ocr_text}"
            return text.strip(), True if text.strip() else False
        except Exception as e:
            logging.error(f"OCR failed: {e}")
            return None, False


class DocxInputHandler:
    def extract_text(self, docx_path):
        try:
            doc = Document(docx_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip(), True if text.strip() else False
        except Exception as e:
            logging.error(f"DOCX extraction failed: {e}")
            return None, False


def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        handler = PDFInputHandler()
    elif file_path.endswith(".docx"):
        handler = DocxInputHandler()
    else:
        logging.error("❌ Unsupported file format.")
        return None, False

    return handler.extract_text(file_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <file_path>")
        return

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    text, success = extract_text_from_file(file_path)

    if success:
        print(f"\n✅ Extracted {len(text)} characters.")
        print("📄 First 500 chars preview:\n")
        print(text[:500])
    else:
        print("❌ Extraction failed.")


if __name__ == "__main__":
    main()

        

