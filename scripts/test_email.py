import json
import os

from build_content import build_subject, build_message, resolve_asset, build_share_links
from send_email import send_email

# Load the sample bootcamp calendar
with open("calendar/bootcamp_calendar.json", "r", encoding="utf-8") as f:
    calendar = json.load(f)

# Pick a test case: Week 1, Tuesday
week = 1
day = "Tuesday"
week_plan = calendar["weeks"][week - 1]
day_plan = week_plan["days"][day]

print(f"📅 Testing Day: Week {week}, {day}")
print(f"Post type: {day_plan['post_type']}")

# Build subject, message, and asset
subject = build_subject(week, day, day_plan["post_type"], "TestPlatform")
message = build_message(day_plan)
asset_url = resolve_asset(day_plan)

# Build share links (simulate for LinkedIn only)
share_links = build_share_links(message, asset_url, {"LinkedIn": "12:00"})

print("\n--- SUBJECT ---")
print(subject)

print("\n--- MESSAGE (HTML) ---")
print(message)

print("\n--- ASSET URL ---")
print(asset_url)

print("\n--- SHARE LINKS ---")
print(share_links)

# Send test email
print("\n📧 Sending test email...")
send_email(subject, message, {"LinkedIn": "12:00"}, asset_url)
