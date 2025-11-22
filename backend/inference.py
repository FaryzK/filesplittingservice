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


SIMILARITY_THRESHOLD = 0.95


def find_first_pages(composite_pdf_path: str, embeddings_path: str = None) -> Tuple[List[int], Dict[int, Dict]]:
    """
    Identify first pages in a composite PDF by comparing embeddings.
    
    Args:
        composite_pdf_path: Path to composite PDF file
        embeddings_path: Path to embeddings JSON file
    
    Returns:
        Tuple of (list of page indices, dict of page_idx -> similarity info)
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
    similarity_info = {}  # Store similarity scores for each page
    
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
        
        # Store similarity info for this page (even if no match)
        if matches:
            # Sort by combined score
            matches.sort(key=lambda x: x["combined_score"], reverse=True)
            best_match = matches[0]
            
            # Log similarity scores for debugging
            print(f"Page {page_idx + 1}: Best match = {best_match['filename']}")
            print(f"  Image similarity: {best_match['image_similarity']:.4f} ({best_match['image_similarity']*100:.2f}%)")
            print(f"  Text similarity: {best_match['text_similarity']:.4f} ({best_match['text_similarity']*100:.2f}%)")
            print(f"  Combined score: {best_match['combined_score']:.4f} ({best_match['combined_score']*100:.2f}%)")
            print(f"  Threshold: {SIMILARITY_THRESHOLD:.4f} ({SIMILARITY_THRESHOLD*100:.2f}%)")
            
            # Store similarity info
            similarity_info[page_idx] = {
                "matched": best_match["combined_score"] > SIMILARITY_THRESHOLD,
                "best_match": best_match["filename"],
                "image_similarity": best_match["image_similarity"],
                "text_similarity": best_match["text_similarity"],
                "combined_score": best_match["combined_score"],
                "all_matches": matches  # Store all matches above threshold
            }
            
            if best_match["combined_score"] > SIMILARITY_THRESHOLD:
                print(f"  ✓ MATCHED - Page {page_idx + 1} identified as first page")
                first_pages.append(page_idx)
            else:
                print(f"  ✗ NOT MATCHED - Score below threshold")
        else:
            # No matches found, but store info anyway
            print(f"Page {page_idx + 1}: No matches found (all below threshold)")
            similarity_info[page_idx] = {
                "matched": False,
                "best_match": None,
                "image_similarity": 0.0,
                "text_similarity": 0.0,
                "combined_score": 0.0,
                "all_matches": []
            }
    
    return first_pages, similarity_info


def split_composite_pdf(
    composite_pdf_path: str,
    output_dir: str,
    embeddings_path: str = None
) -> Tuple[List[Dict[str, str]], Dict[int, Dict]]:
    """
    Split a composite PDF into individual documents based on identified first pages.
    
    Args:
        composite_pdf_path: Path to composite PDF file
        output_dir: Directory to save split PDFs
        embeddings_path: Path to embeddings JSON file
    
    Returns:
        Tuple of (list of split documents, similarity info dict)
    """
    # Find first pages
    if embeddings_path is None:
        from utils import get_backend_dir
        embeddings_path = os.path.join(get_backend_dir(), "data", "embeddings.json")
    
    first_pages, similarity_info = find_first_pages(composite_pdf_path, embeddings_path)
    
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
        
        # Create new PDF writer for each split document
        writer = PdfWriter()
        
        # Add only the specific pages we want (from start to end)
        # Don't use clone_reader_document_root as it may include all pages
        print(f"\nCreating Document {i + 1}:")
        print(f"  Start page (0-indexed): {start_page}")
        print(f"  End page (0-indexed): {end_page}")
        print(f"  Pages to include: {list(range(start_page, end_page))}")
        
        for page_num in range(start_page, end_page):
            page = reader.pages[page_num]
            writer.add_page(page)
            print(f"  Added page {page_num + 1} (index {page_num})")
        
        # Verify we have the correct number of pages
        expected_pages = end_page - start_page
        actual_pages = len(writer.pages)
        print(f"  Result: {actual_pages} pages in document (expected {expected_pages})")
        
        if actual_pages != expected_pages:
            print(f"  ERROR: Page count mismatch!")
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(composite_pdf_path))[0]
        output_filename = f"{base_name}_document_{i + 1}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save split PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Get similarity info for the first page of this document
        page_similarity = similarity_info.get(start_page, {})
        
        split_documents.append({
            "filename": output_filename,
            "path": output_path,
            "start_page": start_page + 1,  # 1-indexed for display
            "end_page": end_page,
            "similarity": {
                "matched_document": page_similarity.get("best_match"),
                "image_similarity": round(page_similarity.get("image_similarity", 0.0), 4),
                "text_similarity": round(page_similarity.get("text_similarity", 0.0), 4),
                "combined_score": round(page_similarity.get("combined_score", 0.0), 4)
            }
        })
    
    return split_documents, similarity_info

