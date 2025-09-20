import os
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Environment, FileSystemLoader
from build_content import build_share_links

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO", "").split(",")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


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
                import requests
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
                import requests
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
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
