from send_email import send_email

subject = "Test Bootcamp Automation Email"
text = "🚀 This is a test email from Bootcamp Automation system. This will start working fully from Monday according to the planned scheduled on all the Platforms!. Stay Tuned."
platforms = {"LinkedIn": "07:45", "Facebook": "12:30"}  # Dummy platforms
asset = None  # Or path to an image e.g. "assets/flyers/week1_monday.png"

send_email(subject, text, platforms, asset)

print("✅ Test email sent successfully")