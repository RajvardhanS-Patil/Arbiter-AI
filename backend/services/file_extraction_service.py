"""
Arbiter AI — File Extraction Service
Extracts readable text from uploaded documents (PDF, TXT, DOCX) and images.
"""
import io
from PyPDF2 import PdfReader
from PIL import Image

class FileExtractionService:
    def extract_text(self, filename: str, content: bytes) -> str:
        """Extracts text from various file formats."""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        
        try:
            if ext == "pdf":
                return self._extract_pdf(content)
            elif ext in ["txt", "md", "csv", "json"]:
                return content.decode("utf-8", errors="ignore")
            elif ext in ["png", "jpg", "jpeg"]:
                return self._extract_image(content, filename)
            elif ext == "docx":
                return f"[DOCX File: {filename} - Text extraction needs python-docx, passing as reference]"
            else:
                # Attempt generic text decoding as fallback
                return content.decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"Error extracting text from {filename}: {e}")
            return f"[Failed to extract text from {filename}]"

    def _extract_pdf(self, content: bytes) -> str:
        text = []
        pdf = PdfReader(io.BytesIO(content))
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n".join(text)

    def _extract_image(self, content: bytes, filename: str) -> str:
        # In a real scenario, use Tesseract OCR or send image to Gemini/GPT-4V.
        # For this hackathon, we'll extract basic EXIF data as placeholder context.
        try:
            img = Image.open(io.BytesIO(content))
            desc = f"[Image File: {filename}, Format: {img.format}, Size: {img.size}]"
            return desc
        except:
            return f"[Image File: {filename}]"

file_extraction_service = FileExtractionService()
