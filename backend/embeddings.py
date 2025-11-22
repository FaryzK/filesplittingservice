"""Embedding generation for images and text using CLIP and OpenAI."""
import os
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from PIL import Image
import io
import base64


# Initialize models (lazy loading)
_image_model = None
_openai_client = None


def get_image_model():
    """Get or initialize the CLIP image embedding model."""
    global _image_model
    if _image_model is None:
        print("Loading CLIP model (this may take a few minutes on first run)...")
        _image_model = SentenceTransformer('clip-ViT-L-14')
        print("CLIP model loaded successfully!")
    return _image_model


def get_openai_client():
    """Get or initialize OpenAI client."""
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def generate_image_embedding(image: Image.Image) -> List[float]:
    """
    Generate image embedding using CLIP-ViT-L-14.
    
    Args:
        image: PIL Image
    
    Returns:
        List of float values representing the embedding vector
    """
    model = get_image_model()
    embedding = model.encode(image, convert_to_numpy=True)
    return embedding.tolist()


def generate_text_embedding(text: str) -> List[float]:
    """
    Generate text embedding using OpenAI text-embedding-3-small.
    
    Args:
        text: Text string to embed
    
    Returns:
        List of float values representing the embedding vector
    """
    client = get_openai_client()
    
    # Truncate text if too long (OpenAI has token limits)
    # text-embedding-3-small supports up to 8191 tokens, roughly 30k characters
    max_chars = 30000
    if len(text) > max_chars:
        text = text[:max_chars]
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f"Error generating text embedding: {str(e)}")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two embedding vectors.
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
    
    Returns:
        Cosine similarity score between -1 and 1
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))

