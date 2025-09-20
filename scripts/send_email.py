import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Load environment variables
load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)
EMAIL_TO = os.getenv("EMAIL_TO", "").split(",")


def build_share_links(text: str, asset: str = None, platforms: dict = None):
    """Generate share links only for the given platforms"""
    base_text = text if text else "Check this out!"

    all_links = {
        "LinkedIn": f"https://www.linkedin.com/sharing/share-offsite/?url=https://example.com&summary={base_text}",
        "Facebook": f"https://www.facebook.com/sharer/sharer.php?u=https://example.com&quote={base_text}",
        "X": f"https://twitter.com/intent/tweet?text={base_text}",
        "Instagram": "https://www.instagram.com/",  # Instagram doesn't support direct prefilled share
        "TikTok": "https://www.tiktok.com/",        # TikTok requires in-app sharing
        "WhatsApp": f"https://wa.me/?text={base_text}"
    }

    if platforms:
        return {p: all_links[p] for p in platforms.keys() if p in all_links}
    return all_links


def build_email_html(subject: str, text: str, platforms: dict, asset: str = None):
    """Render HTML email using Jinja2 template"""
    env = Environment(loader=FileSystemLoader("scripts/templates"))
    template = env.get_template("email_template.html")

    share_links = build_share_links(text, asset, platforms)

    return template.render(
        subject=subject,
        message=text,
        share_links=share_links,
        platforms=platforms,
        asset=asset
    )


def send_email(subject: str, text: str, platforms: dict, asset: str = None):
    """Send email with optional attachment"""
    # Create MIME message
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject

    # HTML body
    html_body = build_email_html(subject, text, platforms, asset)
    msg.attach(MIMEText(html_body, "html"))

    # Attach asset if provided (flyer/image/video)
    if asset and os.path.exists(asset):
        with open(asset, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(asset)}")
        msg.attach(part)

    # Send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"✅ Email sent successfully to {EMAIL_TO}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
