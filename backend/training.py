"""Training pipeline for processing individual documents and storing embeddings."""
import os
from typing import Dict, Tuple
from pdf_processor import pdf_to_images, extract_text_from_page
from content_detector import detect_content_area, crop_to_content, get_content_area_with_visualization
from embeddings import generate_image_embedding, generate_text_embedding
from utils import add_training_embedding


def process_training_document(pdf_path: str, filename: str) -> Dict:
    """
    Process a training document: detect content area, generate embeddings, and store.
    
    Args:
        pdf_path: Path to the PDF file
        filename: Name of the file (used as key in embeddings storage)
    
    Returns:
        Dictionary containing processing results including bbox and visualization data
    """
    print(f"Processing training document: {filename}")
    
    # Get first page as image
    print("Converting PDF to image...")
    images = pdf_to_images(pdf_path)
    if not images:
        raise ValueError("PDF has no pages")
    
    first_page_image = images[0]
    
    # Detect content area
    print("Detecting content area...")
    bbox = detect_content_area(first_page_image)
    cropped_image = crop_to_content(first_page_image, bbox)
    
    # Generate embeddings
    print("Generating image embedding...")
    image_embedding = generate_image_embedding(cropped_image)
    print("Generating text embedding...")
    text = extract_text_from_page(pdf_path, 0)
    text_embedding = generate_text_embedding(text)
    
    # Store embeddings
    print("Storing embeddings...")
    add_training_embedding(filename, image_embedding, text_embedding, bbox)
    
    print(f"Training complete for {filename}!")
    
    # Return results for visualization
    return {
        "filename": filename,
        "bbox": bbox,
        "original_image": first_page_image,
        "cropped_image": cropped_image,
        "status": "success"
    }


def get_training_pipeline_preview(pdf_path: str) -> Dict:
    """
    Get preview of training pipeline (for visualization in frontend).
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Dictionary containing original image, bbox, and cropped image
    """
    images = pdf_to_images(pdf_path)
    if not images:
        raise ValueError("PDF has no pages")
    
    first_page_image = images[0]
    original, bbox, cropped = get_content_area_with_visualization(first_page_image)
    
    return {
        "original_image": original,
        "bbox": bbox,
        "cropped_image": cropped
    }

