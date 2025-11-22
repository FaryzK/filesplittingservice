"""FastAPI application for PDF document splitting."""
import os
import sys
import shutil
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
backend_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

# Add backend directory to path for imports
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from training import process_training_document, get_training_pipeline_preview
from inference import split_composite_pdf
from utils import ensure_directory, load_embeddings
from PIL import Image
import io
import base64

app = FastAPI(title="PDF Document Splitter API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
# Use absolute paths based on backend directory
uploads_training = os.path.join(backend_dir, "uploads", "training")
uploads_inference = os.path.join(backend_dir, "uploads", "inference")
outputs_dir = os.path.join(backend_dir, "outputs")
data_dir = os.path.join(backend_dir, "data")

ensure_directory(uploads_training)
ensure_directory(uploads_inference)
ensure_directory(outputs_dir)
ensure_directory(data_dir)


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


@app.get("/")
async def root():
    return {"message": "PDF Document Splitter API"}


@app.post("/api/train")
async def train_model(file: UploadFile = File(...)):
    """
    Upload an individual document for training.
    Returns pipeline visualization data.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file
    upload_path = os.path.join(uploads_training, file.filename)
    ensure_directory(os.path.dirname(upload_path))
    
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process training document
        result = process_training_document(upload_path, file.filename)
        
        # Convert images to base64 for frontend
        original_b64 = image_to_base64(result["original_image"])
        cropped_b64 = image_to_base64(result["cropped_image"])
        
        return {
            "status": "success",
            "filename": result["filename"],
            "bbox": result["bbox"],
            "original_image": original_b64,
            "cropped_image": cropped_b64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing training document: {str(e)}")


@app.post("/api/inference")
async def run_inference(file: UploadFile = File(...)):
    """
    Upload a composite PDF for splitting.
    Returns list of split documents.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file
    upload_path = os.path.join(uploads_inference, file.filename)
    ensure_directory(os.path.dirname(upload_path))
    
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Split composite PDF
        output_dir = outputs_dir
        split_docs, similarity_info = split_composite_pdf(upload_path, output_dir)
        
        # Return list of split documents (similarity scores are logged, not returned)
        return {
            "status": "success",
            "split_documents": [
                {
                    "filename": doc["filename"],
                    "start_page": doc["start_page"],
                    "end_page": doc["end_page"]
                }
                for doc in split_docs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing inference: {str(e)}")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """
    Download a split PDF file.
    """
    file_path = os.path.join(outputs_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )


@app.get("/api/training-status")
async def get_training_status():
    """
    Get status of training data (list of trained documents).
    """
    embeddings = load_embeddings()
    
    # Return documents with their preview info
    documents = []
    for filename, data in embeddings.items():
        documents.append({
            "filename": filename,
            "bbox": data.get("bbox"),
            "has_preview": bool(data.get("original_image_path") and data.get("cropped_image_path"))
        })
    
    return {
        "trained_documents": documents,
        "count": len(embeddings)
    }


@app.get("/api/training-preview/{filename:path}")
async def get_training_preview(filename: str):
    """
    Get saved pipeline preview for a trained document.
    """
    from urllib.parse import unquote
    # Decode URL-encoded filename
    filename = unquote(filename)
    
    embeddings = load_embeddings()
    
    if filename not in embeddings:
        raise HTTPException(status_code=404, detail="Document not found in training data")
    
    doc_data = embeddings[filename]
    original_path = doc_data.get("original_image_path")
    cropped_path = doc_data.get("cropped_image_path")
    
    if not original_path or not cropped_path:
        raise HTTPException(status_code=404, detail="Preview images not found for this document")
    
    if not os.path.exists(original_path) or not os.path.exists(cropped_path):
        raise HTTPException(status_code=404, detail="Preview image files not found")
    
    # Load and convert images to base64
    from PIL import Image
    original_img = Image.open(original_path)
    cropped_img = Image.open(cropped_path)
    
    original_b64 = image_to_base64(original_img)
    cropped_b64 = image_to_base64(cropped_img)
    
    return {
        "filename": filename,
        "bbox": doc_data.get("bbox"),
        "original_image": original_b64,
        "cropped_image": cropped_b64
    }


@app.post("/api/preview-pipeline")
async def preview_pipeline(file: UploadFile = File(...)):
    """
    Preview the training pipeline without saving embeddings.
    Useful for the Model screen to show content detection.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file temporarily
    upload_path = os.path.join(uploads_training, f"preview_{file.filename}")
    ensure_directory(os.path.dirname(upload_path))
    
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Get pipeline preview
        preview = get_training_pipeline_preview(upload_path)
        
        # Convert images to base64
        original_b64 = image_to_base64(preview["original_image"])
        cropped_b64 = image_to_base64(preview["cropped_image"])
        
        # Clean up temp file
        if os.path.exists(upload_path):
            os.remove(upload_path)
        
        return {
            "status": "success",
            "bbox": preview["bbox"],
            "original_image": original_b64,
            "cropped_image": cropped_b64
        }
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(upload_path):
            os.remove(upload_path)
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

