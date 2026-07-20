#!/usr/bin/env python3
"""
Render contribution data as an animated heatmap SVG.
Reads data/contributions.json, writes contrib-heatmap.svg.
"""

import os
import json
import math
from datetime import datetime, timezone, date, timedelta

# Constants
SVG_W = 860
SVG_H = 280
CELL_SIZE = 12
CELL_GAP = 2
MONTH_LABEL_H = 14
DAY_LABEL_W = 30
TOP_PAD = 20
LEFT_PAD = 35
RIGHT_PAD = 20
BOTTOM_PAD = 50

# GitHub-ish green palette
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#           none        level 1   level 2   level 3   level 4   level 5

BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b949e"
STATS_COLOR = "#c9d1d9"
ACCENT_COLOR = "#39d353"

INPUT_PATH = "data/contributions.json"
OUTPUT_PATH = "contrib-heatmap.svg"


def load_data(path=INPUT_PATH):
    """Load contribution data from JSON."""
    if not os.path.exists(path):
        print(f"Error: {path} not found. Run fetch_contributions.py first.")
        return None
    
    with open(path) as f:
        data = json.load(f)
    
    return data


def get_weekday_labels():
    """Return day labels for the heatmap (Mon, Wed, Fri)."""
    return [(1, "Mon"), (3, "Wed"), (5, "Fri")]


def build_calendar_grid(contributions):
    """Build a 53-week x 7-day grid from contribution data."""
    # Build date -> count/level lookup
    contrib_map = {}
    for c in contributions:
        contrib_map[c["date"]] = {"count": c["count"], "level": c["level"]}
    
    # Find the last Sunday (end of the contribution calendar)
    today = date.today()
    # GitHub calendar ends on the last Saturday
    end_date = today
    # Go back to find the Saturday of the current week
    while end_date.weekday() != 5:  # Saturday
        end_date -= timedelta(days=1)
    
    # Start is 52 weeks + 6 days before end (53 weeks total)
    start_date = end_date - timedelta(weeks=52, days=6)
    
    # Build grid: 53 columns (weeks) x 7 rows (days)
    # Row 0 = Sunday, Row 6 = Saturday
    grid = []
    current = start_date
    week = 0
    while current <= end_date:
        day_of_week = current.weekday()
        # Convert: Python Monday=0..Sunday=6 -> Sunday=0..Saturday=6
        sunday_based = (day_of_week + 1) % 7
        
        date_str = current.isoformat()
        entry = contrib_map.get(date_str, {"count": 0, "level": 0})
        
        grid.append({
            "date": date_str,
            "week": week,
            "day": sunday_based,
            "count": entry["count"],
            "level": entry["level"]
        })
        
        if sunday_based == 6:  # Saturday -> next week
            week += 1
        
        current += timedelta(days=1)
    
    return grid, start_date, end_date


def generate_svg(data, output_path=OUTPUT_PATH):
    """Generate animated heatmap SVG."""
    contributions = data["contributions"]
    stats = data["stats"]
    
    grid, start_date, end_date = build_calendar_grid(contributions)
    
    # Calculate grid dimensions
    max_week = max(c["week"] for c in grid) + 1 if grid else 53
    num_weeks = min(max_week, 53)
    
    # Cell positions
    cell_w = CELL_SIZE + CELL_GAP
    cell_h = CELL_SIZE + CELL_GAP
    
    # SVG content
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">')
    lines.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}" rx="8"/>')
    
    # Month labels - sort by week position to maintain correct order
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_positions = {}
    for c in grid:
        month = int(c["date"][5:7])
        week = c["week"]
        if month not in month_positions or week < month_positions[month]:
            month_positions[month] = week
    
    for month_num, week_idx in sorted(month_positions.items(), key=lambda x: x[1]):
        x = LEFT_PAD + week_idx * cell_w
        lines.append(f'  <text x="{x}" y="{TOP_PAD - 5}" font-family="monospace" font-size="10" fill="{TEXT_COLOR}">'
                     f'{months[month_num - 1]}</text>')
    
    # Day labels
    for day_num, label in get_weekday_labels():
        y = TOP_PAD + MONTH_LABEL_H + day_num * cell_h + cell_h / 2 + 3
        lines.append(f'  <text x="{LEFT_PAD - 5}" y="{y}" font-family="monospace" font-size="9" fill="{TEXT_COLOR}" '
                     f'text-anchor="end">{label}</text>')
    
    # Contribution cells with diagonal reveal animation
    total_cells = len(grid)
    anim_delay_per_cell = 0.002  # seconds per cell
    base_delay = 0.3
    
    for i, c in enumerate(grid):
        x = LEFT_PAD + c["week"] * cell_w
        y = TOP_PAD + MONTH_LABEL_H + c["day"] * cell_h
        level = min(c["level"], len(PALETTE) - 1)
        color = PALETTE[level]
        
        # Diagonal reveal: cells closer to top-left appear first
        delay = base_delay + (c["week"] + c["day"]) * 0.008
        
        lines.append(f'  <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" fill="{color}" opacity="0">')
        lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.15s" begin="{delay:.3f}s" fill="freeze"/>')
        lines.append(f'  </rect>')
    
    # Legend
    legend_x = LEFT_PAD
    legend_y = SVG_H - BOTTOM_PAD + 15
    
    lines.append(f'  <text x="{legend_x}" y="{legend_y}" font-family="monospace" font-size="10" fill="{TEXT_COLOR}">Less</text>')
    
    for i, color in enumerate(PALETTE):
        lx = legend_x + 40 + i * (CELL_SIZE + CELL_GAP + 2)
        lines.append(f'  <rect x="{lx}" y="{legend_y - 8}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="2" fill="{color}"/>')
    
    lines.append(f'  <text x="{legend_x + 40 + len(PALETTE) * (CELL_SIZE + CELL_GAP + 2)}" y="{legend_y}" '
                 f'font-family="monospace" font-size="10" fill="{TEXT_COLOR}">More</text>')
    
    # Stats footer
    stats_y = legend_y + 25
    total = stats["total"]
    streak = stats["current_streak"]
    best_day = stats["best_day"]
    
    stats_text = f"~{total:,} contributions in the last year"
    if streak > 0:
        stats_text += f"  ·  {streak}-day streak"
    if best_day["count"] > 0:
        stats_text += f"  ·  Best: {best_day['count']} on {best_day['date']}"
    
    lines.append(f'  <text x="{LEFT_PAD}" y="{stats_y}" font-family="monospace" font-size="11" fill="{STATS_COLOR}" opacity="0">')
    lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{base_delay + total_cells * anim_delay_per_cell:.2f}s" fill="freeze"/>')
    lines.append(f'    {stats_text}')
    lines.append(f'  </text>')
    
    # Updated timestamp
    updated = stats.get("updated_at", datetime.now(timezone.utc).isoformat())[:10]
    lines.append(f'  <text x="{LEFT_PAD}" y="{stats_y + 18}" font-family="monospace" font-size="9" fill="{TEXT_COLOR}" opacity="0">')
    lines.append(f'    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{base_delay + total_cells * anim_delay_per_cell + 0.3:.2f}s" fill="freeze"/>')
    lines.append(f'    Last updated: {updated}')
    lines.append(f'  </text>')
    
    lines.append('</svg>')
    
    svg_content = "\n".join(lines)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"  Wrote {output_path} ({len(grid)} cells, {num_weeks} weeks)")
    return output_path


def main():
    data = load_data()
    if not data:
        return
    
    generate_svg(data)
    print("Done!")


if __name__ == "__main__":
    main()