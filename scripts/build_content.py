import os


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
    """
    return day_plan.get("text", f"📢 {day_plan['post_type']}")


def resolve_asset(day_plan: dict) -> str:
    """
    Resolve the asset path if provided.
    Returns None if no asset exists.
    """
    asset = day_plan.get("asset")
    if asset and os.path.exists(asset):
        return asset
    return None
