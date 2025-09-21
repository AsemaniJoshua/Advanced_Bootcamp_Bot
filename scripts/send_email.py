import os
import smtplib
import mimetypes
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Environment, FileSystemLoader
from build_content import build_share_links
from dotenv import load_dotenv

# Loading environments
load_dotenv()

# --- Environment Validation ---
required_env_vars = ["EMAIL_FROM", "EMAIL_TO", "EMAIL_HOST", "EMAIL_USER", "EMAIL_PASS"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"❌ Missing required environment variables: {', '.join(missing_vars)}")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO", "").split(",")
SMTP_SERVER = os.getenv("EMAIL_HOST")
SMTP_PORT = int(os.getenv("EMAIL_PORT", 587))  # Default to 587 for STARTTLS
SMTP_USER = os.getenv("EMAIL_USER")
SMTP_PASS = os.getenv("EMAIL_PASS")


def build_email_html(subject: str, text: str, platforms: dict, asset_url: str = None):
    """Render HTML email with optional inline image and share links"""
    env = Environment(loader=FileSystemLoader("scripts/templates"))
    template = env.get_template("email_template.html")

    share_links = build_share_links(text, asset_url, platforms)

    return template.render(
        subject=subject,
        message=text,
        share_links=share_links,
        asset=asset_url
    )


def send_email(subject: str, text: str, platforms: dict, asset: str = None):
    """Send email with optional inline image or attachment"""
    # print(">>> send_email.py loaded")  # Add this at the top
    msg = MIMEMultipart("related")  # allows HTML + images
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject

    # Create alternative for HTML
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)

    # Build HTML body
    html_body = build_email_html(subject, text, platforms, asset)
    msg_alt.attach(MIMEText(html_body, "html"))

    # If asset exists, decide how to include it
    if asset:
        mime_type, _ = mimetypes.guess_type(asset)
        if mime_type and mime_type.startswith("image"):
            try:
                # Fetch raw image (works if asset is GitHub-hosted URL)
                
                resp = requests.get(asset)
                resp.raise_for_status()
                img_data = resp.content

                img = MIMEImage(img_data)
                img.add_header("Content-ID", "<inline-image>")
                img.add_header("Content-Disposition", "inline", filename=os.path.basename(asset))
                msg.attach(img)
            except Exception as e:
                print(f"⚠️ Could not embed image inline: {e}")
        else:
            # Fallback: attach non-image file (e.g., video)
            try:
                
                resp = requests.get(asset, stream=True)
                resp.raise_for_status()
                file_data = resp.content

                base = MIMEBase("application", "octet-stream")
                base.set_payload(file_data)
                encoders.encode_base64(base)
                base.add_header("Content-Disposition", f"attachment; filename={os.path.basename(asset)}")
                msg.attach(base)
            except Exception as e:
                print(f"⚠️ Could not attach asset: {e}")

    # Send email
    try:
        
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
