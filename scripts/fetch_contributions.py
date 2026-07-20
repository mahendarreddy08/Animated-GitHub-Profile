#!/usr/bin/env python3
"""
Fetch GitHub contribution data from public HTML (no token needed).
Parses https://github.com/users/<username>/contributions
Writes data/contributions.json
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta, date
import requests
from bs4 import BeautifulSoup

USERNAME = "mahendarreddy08"
OUTPUT_PATH = "data/contributions.json"


def fetch_contributions(username=USERNAME):
    """Fetch and parse contribution calendar HTML."""
    url = f"https://github.com/users/{username}/contributions"
    print(f"Fetching {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ProfileBot/1.0)"
    }
    
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Find all contribution day cells (td with data-date)
    days = soup.find_all("td", attrs={"data-date": True})
    
    if not days:
        print("  Could not find contribution cells!")
        return []
    
    print(f"  Found {len(days)} contribution days")
    
    # Build a lookup from tool-tip elements (they contain the count text)
    # tool-tip elements have a 'for' attribute matching the td's id
    tooltips = {}
    for tip in soup.select("tool-tip"):
        tip_for = tip.get("for", "")
        tip_text = tip.get_text(strip=True)
        # Parse "X contributions on YYYY-MM-DD" or "No contributions on YYYY-MM-DD"
        if tip_text:
            parts = tip_text.split()
            if parts and parts[0].isdigit():
                tooltips[tip_for] = int(parts[0])
            elif tip_text.startswith("No"):
                tooltips[tip_for] = 0
    
    contributions = []
    for day in days:
        date_str = day.get("data-date")
        level_str = day.get("data-level", "0")
        day_id = day.get("id", "")
        
        # Get count from tooltip lookup, or default to 0
        count = tooltips.get(day_id, 0)
        
        if date_str:
            try:
                contributions.append({
                    "date": date_str,
                    "count": count,
                    "level": int(level_str)
                })
            except ValueError:
                pass
    
    return contributions


def compute_stats(contributions):
    """Compute derived stats from contributions."""
    # Sort by date
    sorted_days = sorted(contributions, key=lambda x: x["date"])
    
    total = sum(d["count"] for d in sorted_days)
    
    # Current streak (from today going back)
    today = date.today()
    current_streak = 0
    check_date = today
    
    # Build a lookup
    contrib_map = {}
    for d in sorted_days:
        contrib_map[d["date"]] = d["count"]
    
    # Count backwards from today
    while True:
        date_str = check_date.isoformat()
        count = contrib_map.get(date_str, 0)
        if count > 0:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Longest streak
    longest_streak = 0
    current_run = 0
    for d in sorted_days:
        if d["count"] > 0:
            current_run += 1
            longest_streak = max(longest_streak, current_run)
        else:
            current_run = 0
    
    # Best day
    best_day = max(sorted_days, key=lambda x: x["count"]) if sorted_days else {"date": today.isoformat(), "count": 0}
    
    # Monthly totals (last 12 months)
    monthly = {}
    for d in sorted_days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]
    
    stats = {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    return stats


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    contributions = fetch_contributions()
    
    if not contributions:
        print("Error: No contribution data found!")
        sys.exit(1)
    
    stats = compute_stats(contributions)
    
    data = {
        "username": USERNAME,
        "contributions": contributions,
        "stats": stats
    }
    
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"  Saved {len(contributions)} contribution days to {OUTPUT_PATH}")
    print(f"  Stats: {stats['total']} total, {stats['current_streak']}-day streak, "
          f"best day: {stats['best_day']['date']} ({stats['best_day']['count']})")
    
    return data


if __name__ == "__main__":
    main()