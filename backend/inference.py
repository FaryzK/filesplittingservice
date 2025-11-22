"""Inference pipeline for splitting composite PDFs based on training embeddings."""
import os
from typing import List, Dict, Tuple
# Use pypdf (better maintained) if available, fallback to PyPDF2
try:
    from pypdf import PdfReader, PdfWriter
    USE_PYPDF = True
except ImportError:
    from PyPDF2 import PdfReader, PdfWriter
    USE_PYPDF = False
from pdf_processor import pdf_to_images, extract_text_from_pdf
from content_detector import detect_content_area, crop_to_content
from embeddings import generate_image_embedding, generate_text_embedding, cosine_similarity
from utils import load_embeddings


SIMILARITY_THRESHOLD = 0.85


def find_first_pages(composite_pdf_path: str, embeddings_path: str = None) -> List[int]:
    """
    Identify first pages in a composite PDF by comparing embeddings.
    
    Args:
        composite_pdf_path: Path to composite PDF file
        embeddings_path: Path to embeddings JSON file
    
    Returns:
        List of page indices (0-indexed) that are identified as first pages
    """
    # Load training embeddings
    if embeddings_path is None:
        from utils import get_backend_dir
        embeddings_path = os.path.join(get_backend_dir(), "data", "embeddings.json")
    
    training_embeddings = load_embeddings(embeddings_path)
    
    if not training_embeddings:
        raise ValueError("No training embeddings found. Please train the model first.")
    
    # Convert PDF to images and extract text
    page_images = pdf_to_images(composite_pdf_path)
    page_texts = extract_text_from_pdf(composite_pdf_path)
    
    first_pages = []
    
    # Process each page
    for page_idx in range(len(page_images)):
        page_image = page_images[page_idx]
        
        # Detect content area and crop
        bbox = detect_content_area(page_image)
        cropped_image = crop_to_content(page_image, bbox)
        
        # Generate embeddings for this page
        page_image_embedding = generate_image_embedding(cropped_image)
        page_text = page_texts[page_idx] if page_idx < len(page_texts) else ""
        page_text_embedding = generate_text_embedding(page_text)
        
        # Compare with training embeddings
        best_match = None
        best_similarity = 0.0
        matches = []
        
        for filename, training_data in training_embeddings.items():
            train_image_emb = training_data["image_embedding"]
            train_text_emb = training_data["text_embedding"]
            
            # Calculate image similarity
            image_sim = cosine_similarity(page_image_embedding, train_image_emb)
            
            if image_sim > SIMILARITY_THRESHOLD:
                # Calculate text similarity for disambiguation
                text_sim = cosine_similarity(page_text_embedding, train_text_emb)
                matches.append({
                    "filename": filename,
                    "image_similarity": image_sim,
                    "text_similarity": text_sim,
                    "combined_score": (image_sim * 0.7) + (text_sim * 0.3)  # Weighted combination
                })
        
        # If we have matches, use the best one
        if matches:
            # Sort by combined score
            matches.sort(key=lambda x: x["combined_score"], reverse=True)
            best_match = matches[0]
            
            if best_match["combined_score"] > SIMILARITY_THRESHOLD:
                first_pages.append(page_idx)
    
    return first_pages


def split_composite_pdf(
    composite_pdf_path: str,
    output_dir: str,
    embeddings_path: str = None
) -> List[Dict[str, str]]:
    """
    Split a composite PDF into individual documents based on identified first pages.
    
    Args:
        composite_pdf_path: Path to composite PDF file
        output_dir: Directory to save split PDFs
        embeddings_path: Path to embeddings JSON file
    
    Returns:
        List of dictionaries with 'filename' and 'path' for each split document
    """
    # Find first pages
    if embeddings_path is None:
        from utils import get_backend_dir
        embeddings_path = os.path.join(get_backend_dir(), "data", "embeddings.json")
    
    first_pages = find_first_pages(composite_pdf_path, embeddings_path)
    
    if not first_pages:
        raise ValueError("No first pages identified. Cannot split PDF.")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read composite PDF
    reader = PdfReader(composite_pdf_path)
    total_pages = len(reader.pages)
    
    # Add end marker (total pages) to simplify splitting logic
    first_pages.append(total_pages)
    
    split_documents = []
    
    # Split PDF at identified boundaries
    for i in range(len(first_pages) - 1):
        start_page = first_pages[i]
        end_page = first_pages[i + 1]
        
        # Create new PDF writer
        writer = PdfWriter()
        
        # Clone reader to preserve document structure and resources (fonts, images, etc.)
        # This is crucial for preserving formatting
        if USE_PYPDF:
            writer.clone_reader_document_root(reader)
        else:
            # For PyPDF2, try to clone document root if method exists
            if hasattr(writer, 'clone_reader_document_root'):
                writer.clone_reader_document_root(reader)
        
        # Add pages from start to end (exclusive)
        # Cloning the document root first helps preserve all resources
        for page_num in range(start_page, end_page):
            page = reader.pages[page_num]
            writer.add_page(page)
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(composite_pdf_path))[0]
        output_filename = f"{base_name}_document_{i + 1}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save split PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        split_documents.append({
            "filename": output_filename,
            "path": output_path,
            "start_page": start_page + 1,  # 1-indexed for display
            "end_page": end_page
        })
    
    return split_documents

