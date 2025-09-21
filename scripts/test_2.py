import json
import os

from build_content import build_subject, build_message, resolve_asset, build_share_links
from send_email import send_email

# Load the bootcamp calendar
with open("calendar/bootcamp_calendar.json", "r", encoding="utf-8") as f:
    calendar = json.load(f)

# Pick Week 1
week = 1
week_plan = calendar["weeks"][week - 1]

print(f"📅 Running tests for Week {week}...")

for day, day_plan in week_plan["days"].items():
    print("\n==============================")
    print(f"▶ Testing Day: {day}")
    print(f"Post type: {day_plan['post_type']}")

    # Use the first platform key as a test platform
    first_platform = list(day_plan["platforms"].keys())[0]

    # Build subject, message, and asset
    subject = build_subject(week, day, day_plan["post_type"], first_platform)
    message = build_message(day_plan)
    asset_url = resolve_asset(day_plan)

    # Build share links for the first platform
    share_links = build_share_links(message, asset_url, {first_platform: day_plan["platforms"][first_platform]})

    print("\n--- SUBJECT ---")
    print(subject)

    print("\n--- MESSAGE (HTML) ---")
    print(message)

    print("\n--- ASSET URL ---")
    print(asset_url)

    print("\n--- SHARE LINKS ---")
    print(share_links)

    # Send test email for this day
    print("\n📧 Sending test email...")
    send_email(subject, message, {first_platform: day_plan["platforms"][first_platform]}, asset_url)

print("\n✅ Finished sending test emails for all days in Week 1.")
