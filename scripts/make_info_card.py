#!/usr/bin/env python3
"""
Generate a neofetch-style info card SVG.
Writes info-card.svg with fade-in line-by-line animation.
Set STATIC=1 env var for a frozen frame preview.
"""

import os

# Card dimensions
CARD_W = 490
CARD_H = 530

# Colors
BG_COLOR = "#0d1117"
TITLE_COLOR = "#39d353"  # green
KEY_COLOR = "#58a6ff"    # blue
VAL_COLOR = "#c9d1d9"    # light gray
DIM_COLOR = "#8b949e"    # dim gray
ACCENT_COLOR = "#f0883e" # orange
SEPARATOR_COLOR = "#21262d"

# User info - customize these!
USERNAME = "mahendarreddy08"
STACK = "Python · JavaScript · React · Node.js · SQL"
HIGHLIGHTS = [
    "Open-source contributor",
    "Building CLI tools & web apps",
    "Automation & DevOps enthusiast",
    "Always learning"
]
NOW = "Building cool stuff with Python & JS"
PREV = "Exploring AI/ML & system design"

STATIC = os.environ.get("STATIC") == "1"


def generate_svg(output_path="info-card.svg"):
    """Generate neofetch-style info card SVG."""
    
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}">')
    lines.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}" rx="8"/>')
    
    # Title bar
    title_y = 40
    lines.append(f'  <text x="25" y="{title_y}" font-family="monospace" font-size="14" font-weight="bold" fill="{TITLE_COLOR}">')
    lines.append(f'    mahendarreddy08@github')
    if not STATIC:
        lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.2s" fill="freeze"/>')
    lines.append(f'  </text>')
    
    # Separator line
    sep_y = 55
    lines.append(f'  <line x1="25" y1="{sep_y}" x2="{CARD_W - 25}" y2="{sep_y}" stroke="{SEPARATOR_COLOR}" stroke-width="1"')
    if not STATIC:
        lines.append(f'        stroke-dasharray="440" stroke-dashoffset="440">')
        lines.append(f'    <animate attributeName="stroke-dashoffset" from="440" to="0" dur="0.6s" begin="0.5s" fill="freeze"/>')
    else:
        lines.append(f'/>')
    
    # Info rows: (label, value, color)
    info_rows = [
        ("OS", f"GitHub Profile v1.0", DIM_COLOR),
        ("Host", f"@{USERNAME}", KEY_COLOR),
        ("Uptime", "∞ (always active)", DIM_COLOR),
        ("Shell", "/bin/bash", DIM_COLOR),
        ("", "", None),  # spacer
        ("── Now", "", None),
        ("", NOW, VAL_COLOR),
        ("── Prev", "", None),
        ("", PREV, VAL_COLOR),
        ("", "", None),  # spacer
        ("── Stack", "", None),
        ("", STACK, VAL_COLOR),
        ("", "", None),  # spacer
        ("── Highlights", "", None),
    ]
    
    for h in HIGHLIGHTS:
        info_rows.append(("", f"  • {h}", DIM_COLOR))
    
    # Render rows with staggered fade-in
    row_y = 80
    base_delay = 0.8
    row_delay = 0.12
    
    for i, (label, value, color) in enumerate(info_rows):
        delay = base_delay + i * row_delay
        
        if label == "" and value == "":
            row_y += 10
            continue
        
        if label in ("── Now", "── Prev", "── Stack", "── Highlights"):
            # Section header
            lines.append(f'  <text x="25" y="{row_y}" font-family="monospace" font-size="12" font-weight="bold" fill="{ACCENT_COLOR}"')
            if not STATIC:
                lines.append(f'        opacity="0">')
                lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{delay:.2f}s" fill="freeze"/>')
            else:
                lines.append(f'  >')
            lines.append(f'    {value}')
            lines.append(f'  </text>')
            row_y += 22
            continue
        
        if label:
            # Key: value row
            lines.append(f'  <text x="25" y="{row_y}" font-family="monospace" font-size="12" fill="{KEY_COLOR}"')
            if not STATIC:
                lines.append(f'        opacity="0">')
                lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{delay:.2f}s" fill="freeze"/>')
            else:
                lines.append(f'  >')
            lines.append(f'    {label}')
            lines.append(f'  </text>')
            
            lines.append(f'  <text x="120" y="{row_y}" font-family="monospace" font-size="12" fill="{color}"')
            if not STATIC:
                lines.append(f'        opacity="0">')
                lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{delay + 0.05:.2f}s" fill="freeze"/>')
            else:
                lines.append(f'  >')
            lines.append(f'    {value}')
            lines.append(f'  </text>')
            row_y += 22
        else:
            # Value-only row
            lines.append(f'  <text x="25" y="{row_y}" font-family="monospace" font-size="12" fill="{color}"')
            if not STATIC:
                lines.append(f'        opacity="0">')
                lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{delay:.2f}s" fill="freeze"/>')
            else:
                lines.append(f'  >')
            lines.append(f'    {value}')
            lines.append(f'  </text>')
            row_y += 20
    
    # Bottom separator
    lines.append(f'  <line x1="25" y1="{row_y + 10}" x2="{CARD_W - 25}" y2="{row_y + 10}" stroke="{SEPARATOR_COLOR}" stroke-width="1"')
    if not STATIC:
        lines.append(f'        stroke-dasharray="440" stroke-dashoffset="440">')
        lines.append(f'    <animate attributeName="stroke-dashoffset" from="440" to="0" dur="0.6s" begin="{base_delay + len(info_rows) * row_delay:.2f}s" fill="freeze"/>')
    else:
        lines.append(f'/>')
    
    # Footer
    footer_y = row_y + 35
    lines.append(f'  <text x="25" y="{footer_y}" font-family="monospace" font-size="10" fill="{DIM_COLOR}"')
    if not STATIC:
        lines.append(f'        opacity="0">')
        lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{base_delay + len(info_rows) * row_delay + 0.3:.2f}s" fill="freeze"/>')
    else:
        lines.append(f'  >')
    lines.append(f'    "The best way to predict the future is to create it."')
    lines.append(f'  </text>')
    
    lines.append('</svg>')
    
    svg_content = "\n".join(lines)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"  Wrote {output_path}")
    return output_path


if __name__ == "__main__":
    generate_svg()