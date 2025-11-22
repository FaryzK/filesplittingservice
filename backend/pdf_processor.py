"""PDF processing utilities for converting PDFs to images and extracting text."""
import io
import os
from typing import List, Tuple
from pdf2image import convert_from_path
import pdfplumber
from PIL import Image

# Poppler path - update this if your Poppler is installed elsewhere
POPPLER_PATH = r"C:\Program Files\poppler\poppler-25.11.0\Library\bin"


def pdf_to_images(pdf_path: str, dpi: int = 200) -> List[Image.Image]:
    """
    Convert PDF pages to PIL Images.
    
    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for image conversion (default: 200)
    
    Returns:
        List of PIL Images, one per page
    """
    try:
        # Use Poppler path if it exists, otherwise rely on PATH
        poppler_path = POPPLER_PATH if os.path.exists(POPPLER_PATH) else None
        images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
        return images
    except Exception as e:
        raise Exception(f"Error converting PDF to images: {str(e)}")


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract text from each page of a PDF.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        List of text strings, one per page
    """
    texts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                texts.append(text)
        return texts
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_page(pdf_path: str, page_number: int) -> str:
    """
    Extract text from a specific page of a PDF.
    
    Args:
        pdf_path: Path to PDF file
        page_number: Zero-indexed page number
    
    Returns:
        Text content of the page
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_number < len(pdf.pages):
                text = pdf.pages[page_number].extract_text() or ""
                return text
            else:
                raise ValueError(f"Page {page_number} does not exist in PDF")
    except Exception as e:
        raise Exception(f"Error extracting text from page: {str(e)}")

