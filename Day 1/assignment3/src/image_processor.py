"""
Image Processing Module for Financial Report Analyzer
Handles image loading, preprocessing, and OCR operations
"""

import os
import requests
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from pathlib import Path
import base64
from io import BytesIO
from typing import List, Union, Tuple
import pytesseract
import easyocr

class ImageProcessor:
    def __init__(self, max_size=(1024, 1024)):
        self.max_size = max_size
        self.reader = easyocr.Reader(['en'])
        
    def load_images(self, sources: List[Union[str, Path]]) -> List[Image.Image]:
        """
        Load images from various sources (local files, URLs)
        
        Args:
            sources: List of file paths or URLs
            
        Returns:
            List of PIL Images
        """
        images = []
        
        for source in sources:
            try:
                if isinstance(source, str) and source.startswith(('http://', 'https://')):
                    # Load from URL
                    image = self._load_from_url(source)
                else:
                    # Load from local file
                    image = self._load_from_file(source)
                
                if image:
                    processed_image = self.preprocess_image(image)
                    images.append(processed_image)
                    
            except Exception as e:
                print(f"Error loading image from {source}: {str(e)}")
                
        return images
    
    def _load_from_url(self, url: str) -> Image.Image:
        """Load image from URL"""
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    
    def _load_from_file(self, file_path: Union[str, Path]) -> Image.Image:
        """Load image from local file"""
        return Image.open(file_path)
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better analysis
        - Resize if too large
        - Enhance contrast and sharpness
        - Convert to RGB if needed
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large
        if image.size[0] > self.max_size[0] or image.size[1] > self.max_size[1]:
            image.thumbnail(self.max_size, Image.Resampling.LANCZOS)
        
        # Enhance image quality
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    def extract_text_ocr(self, image: Image.Image) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image: PIL Image
            
        Returns:
            Extracted text string
        """
        try:
            # Convert PIL to numpy array for EasyOCR
            img_array = np.array(image)
            
            # Use EasyOCR for better accuracy
            results = self.reader.readtext(img_array)
            
            # Extract text from results
            text_parts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Only include high-confidence text
                    text_parts.append(text)
            
            return ' '.join(text_parts)
            
        except Exception as e:
            print(f"OCR extraction failed: {str(e)}")
            # Fallback to pytesseract
            try:
                return pytesseract.image_to_string(image)
            except:
                return ""
    
    def detect_charts_and_tables(self, image: Image.Image) -> List[dict]:
        """
        Detect charts, graphs and tables in the image
        
        Returns:
            List of detected regions with their types
        """
        # Convert to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        detected_regions = []
        
        # Detect rectangular regions (potential tables/charts)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filter small regions
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Classify based on aspect ratio and size
                region_type = "table" if 0.5 < aspect_ratio < 2.0 else "chart"
                
                detected_regions.append({
                    'type': region_type,
                    'bbox': (x, y, w, h),
                    'area': area,
                    'aspect_ratio': aspect_ratio
                })
        
        return detected_regions
    
    def image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string for API calls"""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def save_processed_images(self, images: List[Image.Image], output_dir: str):
        """Save processed images to output directory"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, image in enumerate(images):
            filename = f"processed_image_{i+1}.png"
            image.save(output_path / filename)
            print(f"Saved: {filename}")

# Example usage and testing
if __name__ == "__main__":
    processor = ImageProcessor()
    
    # Test with sample images
    sample_images = [
        "data/input_images/balance_sheet.png",
        "data/input_images/financial_charts.png"
    ]
    
    images = processor.load_images(sample_images)
    print(f"Loaded {len(images)} images")
    
    for i, img in enumerate(images):
        print(f"Image {i+1}: {img.size}")
        text = processor.extract_text_ocr(img)
        print(f"Extracted text length: {len(text)}")
        
        regions = processor.detect_charts_and_tables(img)
        print(f"Detected {len(regions)} regions")