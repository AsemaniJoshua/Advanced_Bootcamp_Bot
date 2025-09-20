import feedparser
import random

FEEDS = [
    "https://dev.to/feed",              # Dev.to trending posts
    "https://hnrss.org/frontpage",      # Hacker News frontpage
    "https://www.reddit.com/r/webdev/.rss"  # Reddit Webdev community
]

def fetch_curated_article():
    """
    Fetch a trending web dev / programming article from open RSS feeds.
    Returns a dict with {title, url, source}.
    """
    try:
        feed_url = random.choice(FEEDS)
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            return {
                "title": "No trending article found",
                "url": "https://developer.mozilla.org/",
                "source": "MDN Web Docs"
            }

        # Pick one of the top few entries to keep variety
        entry = random.choice(feed.entries[:5])

        return {
            "title": entry.title,
            "url": entry.link,
            "source": feed.feed.title if "title" in feed.feed else "Unknown Source"
        }

    except Exception as e:
        print(f"❌ Error fetching RSS feed: {e}")
        return {
            "title": "Fallback article – Learn web development",
            "url": "https://developer.mozilla.org/en-US/docs/Learn",
            "source": "MDN"
        }
