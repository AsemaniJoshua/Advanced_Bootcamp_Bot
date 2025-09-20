import os
from fetch_articles import fetch_curated_article
import html



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
