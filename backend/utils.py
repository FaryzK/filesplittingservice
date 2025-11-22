"""Utility functions for file handling and data management."""
import json
import os
from pathlib import Path
from typing import Dict, List, Any


def get_backend_dir():
    """Get the backend directory path."""
    current_file = os.path.abspath(__file__)
    return os.path.dirname(current_file)


def ensure_directory(path: str):
    """Ensure a directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)


def load_embeddings(embeddings_path: str = None) -> Dict[str, Any]:
    """
    Load embeddings from JSON file.
    
    Args:
        embeddings_path: Path to embeddings JSON file
    
    Returns:
        Dictionary containing embeddings data
    """
    if embeddings_path is None:
        embeddings_path = os.path.join(get_backend_dir(), "data", "embeddings.json")
    
    if not os.path.exists(embeddings_path):
        return {}
    
    try:
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # If file is empty, return empty dict
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        # If JSON is invalid, return empty dict and optionally fix the file
        print(f"Warning: Invalid JSON in {embeddings_path}, initializing empty embeddings.")
        return {}
    except Exception as e:
        raise Exception(f"Error loading embeddings: {str(e)}")


def save_embeddings(embeddings_data: Dict[str, Any], embeddings_path: str = None):
    """
    Save embeddings to JSON file.
    
    Args:
        embeddings_data: Dictionary containing embeddings data
        embeddings_path: Path to embeddings JSON file
    """
    if embeddings_path is None:
        embeddings_path = os.path.join(get_backend_dir(), "data", "embeddings.json")
    
    ensure_directory(os.path.dirname(embeddings_path))
    
    try:
        with open(embeddings_path, 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise Exception(f"Error saving embeddings: {str(e)}")


def add_training_embedding(
    filename: str,
    image_embedding: List[float],
    text_embedding: List[float],
    bbox: tuple,
    embeddings_path: str = None
):
    """
    Add a new training embedding to the storage.
    
    Args:
        filename: Name of the training document
        image_embedding: Image embedding vector
        text_embedding: Text embedding vector
        bbox: Bounding box of content area (x, y, w, h)
        embeddings_path: Path to embeddings JSON file
    """
    if embeddings_path is None:
        embeddings_path = os.path.join(get_backend_dir(), "data", "embeddings.json")
    
    embeddings_data = load_embeddings(embeddings_path)
    
    embeddings_data[filename] = {
        "image_embedding": image_embedding,
        "text_embedding": text_embedding,
        "bbox": bbox,
        "filename": filename
    }
    
    save_embeddings(embeddings_data, embeddings_path)

