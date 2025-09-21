import os
from fetch_articles import fetch_curated_article
import html
from urllib.parse import quote



def build_subject(week: int, day: str, post_type: str, platform: str) -> str:
    """
    Build a consistent email subject line.
    Example: [Week 1 - Monday] Bootcamp Promo for LinkedIn
    """
    return f"[Week {week} - {day}] {post_type} for {platform}"


def build_message(day_plan: dict) -> str:
    """
    Prepare the text message for the email.
    If text is provided in the plan, return it.
    If no text, fallback to post_type.
    Return the message content (supports HTML paragraphs & curated articles)"""
    
    text = day_plan.get("text", "")
    content_type = day_plan.get("content_type", "")

    # Case 1: Curated article -> fetch live link
    if content_type == "link":
        article = fetch_curated_article()
        return (
            f"<p>{text}</p>"
            f"<p>📰 <b>{article['title']}</b><br>"
            f"Source: {article['source']}<br>"
            f"<a href='{article['url']}'>Read more</a></p>"
        )

    # Case 2: Preformatted HTML text
    if "<p>" in text or "</p>" in text:
        return text

    # Case 3: Plain text -> wrap safely
    safe_text = html.escape(text)
    return f"<p>{safe_text}</p>"


def resolve_asset(day_plan: dict) -> str:
    """
    Resolve the asset path if provided.
    Returns None if no asset exists.
    """
    asset_path = day_plan.get("asset")
    if not asset_path:
        return None

    username = os.getenv("G_USERNAME")
    repo = os.getenv("G_REPO")
    branch = os.getenv("G_BRANCH", "main")

    return f"https://raw.githubusercontent.com/{username}/{repo}/{branch}/{asset_path}"


def build_share_links(text: str, asset: str = None, platforms: dict = None) -> dict:
    """
    Generate share links only for the given platforms, with optional asset URL.
    - Uses urllib.parse.quote to URL-encode text and URLs.
    - Returns a dict {platform: link} filtered to 'platforms' if provided.
    """
    base_text = text if text else "Check this out!"
    encoded_text = quote(base_text, safe="")
    encoded_url = quote(asset, safe="") if asset else quote("https://example.com", safe="")

    all_links = {
        "LinkedIn": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}&summary={encoded_text}",
        "Facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}&quote={encoded_text}",
        "X": f"https://twitter.com/intent/tweet?text={encoded_text}%20{encoded_url}",
        # Instagram & TikTok don't support prefilled web share reliably; provide the asset/url as fallback
        "Instagram": encoded_url,
        "TikTok": encoded_url,
        "WhatsApp": f"https://api.whatsapp.com/send?text={encoded_text}%20{encoded_url}"
    }

    if platforms:
        # 'platforms' is expected to be a dict of scheduled times; keep only keys that exist in all_links
        return {p: all_links[p] for p in platforms.keys() if p in all_links}

    return all_links