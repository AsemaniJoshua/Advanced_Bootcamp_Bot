import os
import json
import pytz
from datetime import datetime
from dotenv import load_dotenv
from send_email import send_email
from build_content import build_subject, build_message, resolve_asset

# Load environment variables
load_dotenv()

TIMEZONE = os.getenv("TIMEZONE", "UTC")
CALENDAR_FILE = "calendar/bootcamp_calendar.json"
STATE_FILE = "calendar/state.json"  # Keeps track of what was already sent

TOLERANCE_MINUTES = 20  # Prevents duplicate sends if script runs every 30 mins


def load_calendar():
    """Load bootcamp calendar JSON"""
    with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state():
    """Load state to avoid duplicate sends"""
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    """Save updated state"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_current_week(start_date):
    """
    Calculate current bootcamp week number based on start date.
    Adjust start_date = first Monday of week 1.
    """
    today = datetime.now(pytz.timezone(TIMEZONE))
    delta_days = (today.date() - start_date.date()).days
    week_number = (delta_days // 7) + 1
    return week_number


def task_runner(start_date):
    """Main logic to check today’s task and send email"""
    now = datetime.now(pytz.timezone(TIMEZONE))
    current_week = get_current_week(start_date)
    current_day = now.strftime("%A")  # Monday, Tuesday, ...

    calendar = load_calendar()
    state = load_state()

    # Find this week’s plan
    week_plan = next((w for w in calendar["weeks"] if w["week"] == current_week), None)
    if not week_plan:
        print(f"ℹ️ No tasks found for Week {current_week}")
        return

    # Find today’s task
    day_plan = week_plan["days"].get(current_day)
    if not day_plan:
        print(f"ℹ️ No tasks scheduled for {current_day}, Week {current_week}")
        return

    # Loop through platforms and check times
    for platform, scheduled_time in day_plan["platforms"].items():
        times = scheduled_time if isinstance(scheduled_time, list) else [scheduled_time]

        for t in times:
            scheduled = now.replace(
                hour=int(t.split(":")[0]),
                minute=int(t.split(":")[1]),
                second=0,
                microsecond=0
            )

            # Time difference in minutes
            diff = abs((now - scheduled).total_seconds() / 60.0)

            # State key = week-day-platform-time
            state_key = f"W{current_week}-{current_day}-{platform}-{t}"

            if diff <= TOLERANCE_MINUTES and state_key not in state:
                # ✅ Build email content here
                subject = build_subject(current_week, current_day, day_plan["post_type"], platform)
                text = build_message(day_plan)
                asset = resolve_asset(day_plan)

                print(f"📤 Sending {subject}...")
                send_email(subject, text, day_plan["platforms"], asset)

                # Mark as sent
                state[state_key] = True
                save_state(state)


if __name__ == "__main__":
    # Define the start date of Week 1 (e.g., the Monday bootcamp starts)
    # ⚠️ Adjust this to the actual Monday start date of your bootcamp
    bootcamp_start_date = datetime(2025, 9, 22, tzinfo=pytz.UTC)

    task_runner(bootcamp_start_date)
