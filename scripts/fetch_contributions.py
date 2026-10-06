#!/usr/bin/env python3
"""
Scrapes daily contribution statistics from GitHub's public contribution fragment:
https://github.com/users/<username>/contributions
Requires no authentication, token, or GraphQL API quota.
Outputs normalized calendar data and metrics to data/contributions.json.
"""
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "jhaabhijeet864")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print("no calendar cells found -- github markup may have changed", file=sys.stderr)
        sys.exit(1)

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else 0
        days.append({"date": date, "count": count, "level": int(td.get("data-level") or 0)})

    days.sort(key=lambda d: d["date"])
    return days


def compute_current_streak(days):
    if not days:
        return 0, None, None
    idx = len(days) - 1
    # If today hasn't recorded contributions yet, look back to yesterday
    if days[idx]["count"] == 0:
        idx -= 1
    streak = 0
    end_idx = idx
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1
    start_idx = idx + 1
    if streak == 0:
        return 0, None, None
    return streak, days[start_idx]["date"], days[end_idx]["date"]


def compute_longest_streak(days):
    longest = run = 0
    longest_start = longest_end = None
    run_start_idx = None
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run == 0:
                run_start_idx = i
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_idx]["date"]
                longest_end = days[i]["date"]
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(days):
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"]) if days else {"date": "N/A", "count": 0}
    cur_len, cur_start, cur_end = compute_current_streak(days)
    long_len, long_start, long_end = compute_longest_streak(days)

    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    monthly_list = [{"month": k, "total": v} for k, v in sorted(monthly.items())]

    avg_active = round(total / active_days, 1) if active_days else 0.0

    return {
        "username": USERNAME,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": avg_active,
        "range": {"start": days[0]["date"], "end": days[-1]["date"]} if days else {"start": "", "end": ""},
        "current_streak": {
            "length": cur_len,
            "start": cur_start,
            "end": cur_end,
        },
        "longest_streak": {
            "length": long_len,
            "start": long_start,
            "end": long_end,
        },
        "best_day": best,
        "monthly": monthly_list,
        "days": days,
    }


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    days = fetch_days()
    data = build_data(days)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Scraped {len(days)} days for {USERNAME} -> {OUT_PATH}")
    print(f"Total: {data['total_contributions']}, Current streak: {data['current_streak']['length']} days")


if __name__ == "__main__":
    main()
