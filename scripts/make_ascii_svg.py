#!/usr/bin/env python3
"""
Convert a prepped photo into a self-typing monochrome ASCII SVG.
Reads data/source-prepped.png, writes avi-ascii.svg.
"""

import os
import math
from PIL import Image

# ASCII density ramp: bright (sparse) -> dark (dense)
# Leading space clears background to nothing
RAMP = " .`:-=+*cs#%@"

# Output dimensions
COLS = 100
ROWS = 53

# SVG styling
FONT_SIZE = 8
CHAR_W = 6.5   # approximate monospace character width
CHAR_H = 10    # approximate monospace character height
FILL_COLOR = "#c9d1d9"  # GitHub light gray
BG_COLOR = "#0d1117"    # GitHub dark background

# Animation timing (seconds)
ROW_DELAY = 0.04   # delay between rows starting
CHAR_DELAY = 0.003 # delay per character within a row


def image_to_ascii_grid(image_path, cols=COLS, rows=ROWS):
    """Convert image to 2D list of ASCII characters."""
    img = Image.open(image_path).convert("L")
    
    # Resize to character grid
    img_resized = img.resize((cols, rows), Image.LANCZOS)
    pixels = list(img_resized.getdata())
    
    # Map brightness to ASCII ramp
    # 0 (black) -> dense chars, 255 (white) -> sparse chars
    grid = []
    for y in range(rows):
        row_chars = []
        for x in range(cols):
            brightness = pixels[y * cols + x]
            # Invert: dark pixels get dense chars, light pixels get sparse
            idx = int((255 - brightness) / 255 * (len(RAMP) - 1))
            idx = max(0, min(idx, len(RAMP) - 1))
            row_chars.append(RAMP[idx])
        grid.append(row_chars)
    
    return grid


def generate_svg(grid, output_path="avi-ascii.svg"):
    """Generate self-typing animated SVG from ASCII grid."""
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    svg_w = cols * CHAR_W + 20
    svg_h = rows * CHAR_H + 20
    
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w:.0f}" height="{svg_h:.0f}" viewBox="0 0 {svg_w:.0f} {svg_h:.0f}">')
    lines.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}"/>')
    
    # Build each row as a text element with clip-path animation
    for y, row in enumerate(grid):
        row_text = "".join(row)
        row_y = 15 + y * CHAR_H
        
        # Clip path for this row - reveals left to right
        clip_id = f"clip-row-{y}"
        total_delay = y * ROW_DELAY
        duration = len(row) * CHAR_DELAY + 0.3
        
        lines.append(f'  <clipPath id="{clip_id}">')
        lines.append(f'    <rect x="10" y="{row_y - CHAR_H + 2}" width="0" height="{CHAR_H + 2}">')
        lines.append(f'      <animate attributeName="width" from="0" to="{len(row) * CHAR_W}" '
                     f'dur="{duration:.2f}s" begin="{total_delay:.3f}s" fill="freeze"/>')
        lines.append(f'    </rect>')
        lines.append(f'  </clipPath>')
        
        # The text row
        lines.append(f'  <text x="10" y="{row_y}" font-family="monospace" font-size="{FONT_SIZE}" '
                     f'fill="{FILL_COLOR}" clip-path="url(#{clip_id})">{row_text}</text>')
        
        # Cursor effect - small block that follows the reveal
        cursor_id = f"cursor-{y}"
        lines.append(f'  <rect x="10" y="{row_y - CHAR_H + 2}" width="{CHAR_W}" height="{CHAR_H}" '
                     f'fill="{FILL_COLOR}" opacity="0">')
        lines.append(f'    <animate attributeName="opacity" values="0;1;0" '
                     f'dur="0.15s" begin="{total_delay:.3f}s" end="{total_delay + duration:.3f}s" '
                     f'repeatCount="indefinite"/>')
        lines.append(f'    <animate attributeName="x" from="10" to="{10 + len(row) * CHAR_W}" '
                     f'dur="{duration:.2f}s" begin="{total_delay:.3f}s" fill="freeze"/>')
        lines.append(f'  </rect>')
    
    lines.append('</svg>')
    
    svg_content = "\n".join(lines)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"  Wrote {output_path} ({cols}×{rows} chars, {len(grid)} rows)")
    return output_path


def main():
    input_path = "data/source-prepped.png"
    output_path = "avi-ascii.svg"
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run prep_photo.py first.")
        return
    
    print("Converting image to ASCII grid...")
    grid = image_to_ascii_grid(input_path)
    
    print("Generating animated SVG...")
    generate_svg(grid, output_path)
    
    print("Done!")


if __name__ == "__main__":
    main()