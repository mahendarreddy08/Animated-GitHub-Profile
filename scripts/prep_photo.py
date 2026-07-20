#!/usr/bin/env python3
"""
Prep a photo for ASCII conversion:
1. Remove background with rembg
2. Apply CLAHE for local contrast
3. Composite onto white background
Outputs: data/source-prepped.png
"""

import sys
import os
from PIL import Image, ImageFilter
import numpy as np
import cv2

def prep_photo(input_path, output_path="data/source-prepped.png"):
    """Remove background, boost contrast, composite on white."""
    
    print(f"Processing {input_path}...")
    
    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Load image
    img = Image.open(input_path).convert("RGB")
    print(f"  Original size: {img.size}")
    
    # Step 1: Remove background with rembg
    try:
        from rembg import remove
        img_no_bg = remove(img)
        print("  Background removed.")
    except Exception as e:
        print(f"  rembg failed ({e}), using original image.")
        img_no_bg = img.convert("RGBA")
    
    # Step 2: Composite onto white
    white_bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))
    if img_no_bg.mode == "RGBA":
        composite = Image.alpha_composite(white_bg, img_no_bg)
    else:
        composite = img_no_bg.convert("RGBA")
    
    gray = composite.convert("L")
    
    # Step 3: Apply CLAHE for local contrast enhancement
    img_cv = np.array(gray)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img_cv)
    
    # Step 4: Slight sharpen
    enhanced_pil = Image.fromarray(enhanced)
    sharpened = enhanced_pil.filter(ImageFilter.SHARPEN)
    
    # Save
    sharpened.save(output_path)
    print(f"  Saved prepped image to {output_path} ({sharpened.size})")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <input-image> [output-path]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/source-prepped.png"
    prep_photo(input_path, output_path)