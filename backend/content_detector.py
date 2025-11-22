"""Content area detection using OpenCV for identifying document content on pages."""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional


def detect_content_area(image: Image.Image, min_area_ratio: float = 0.01) -> Tuple[int, int, int, int]:
    """
    Detect the content area of a document page using OpenCV.
    This handles cases like IC cards that may be positioned anywhere on an A4 page.
    
    Args:
        image: PIL Image of the page
        min_area_ratio: Minimum area ratio (relative to total image) for content detection
    
    Returns:
        Tuple of (x, y, width, height) bounding box of content area
        If no content detected, returns full image dimensions
    """
    # Convert PIL Image to OpenCV format
    img_array = np.array(image)
    
    # Convert to grayscale if needed
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Method 1: Try edge detection for IC cards (better for small objects on white background)
    # Use Canny edge detection to find card boundaries
    edges = cv2.Canny(gray, 50, 150)
    
    # Dilate edges to connect nearby edges
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    # Find contours from edges
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate minimum area threshold (lower for IC cards)
    total_area = image.width * image.height
    min_area = total_area * min_area_ratio
    
    # Filter contours by area and find the largest valid contour
    valid_contours = [c for c in contours if cv2.contourArea(c) >= min_area]
    
    if valid_contours:
        # Find the largest contour (likely the IC card)
        largest_contour = max(valid_contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
    else:
        # Method 2: Fallback - use adaptive thresholding for documents with text
        # This works better for forms and documents with lots of text
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by area
        valid_contours = [c for c in contours if cv2.contourArea(c) >= min_area]
        
        if not valid_contours:
            # No content detected, return full image
            return (0, 0, image.width, image.height)
        
        # Find bounding box of all valid contours
        all_points = np.concatenate(valid_contours)
        x, y, w, h = cv2.boundingRect(all_points)
    
    # Add padding (10% on each side for better cropping)
    padding_x = int(w * 0.10)
    padding_y = int(h * 0.10)
    
    x = max(0, x - padding_x)
    y = max(0, y - padding_y)
    w = min(image.width - x, w + 2 * padding_x)
    h = min(image.height - y, h + 2 * padding_y)
    
    return (x, y, w, h)


def crop_to_content(image: Image.Image, bbox: Tuple[int, int, int, int]) -> Image.Image:
    """
    Crop image to the specified bounding box.
    
    Args:
        image: PIL Image to crop
        bbox: Tuple of (x, y, width, height)
    
    Returns:
        Cropped PIL Image
    """
    x, y, w, h = bbox
    return image.crop((x, y, x + w, y + h))


def get_content_area_with_visualization(image: Image.Image, min_area_ratio: float = 0.01) -> Tuple[Image.Image, Tuple[int, int, int, int], Image.Image]:
    """
    Detect content area and return original, bounding box info, and cropped image.
    Useful for visualization in the frontend.
    
    Args:
        image: PIL Image of the page
        min_area_ratio: Minimum area ratio for content detection
    
    Returns:
        Tuple of (original_image, bbox, cropped_image)
    """
    bbox = detect_content_area(image, min_area_ratio)
    cropped = crop_to_content(image, bbox)
    return image, bbox, cropped

