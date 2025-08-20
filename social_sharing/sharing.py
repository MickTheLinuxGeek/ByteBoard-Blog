# social_sharing/sharing.py

import os
from mastodon import Mastodon
from atproto import Client


def share_to_mastodon(post_title, post_url):
    """
    Shares a blog post to Mastodon.
    """
    try:
        mastodon = Mastodon(
            client_id=os.environ.get("MASTODON_CLIENT_ID"),
            client_secret=os.environ.get("MASTODON_CLIENT_SECRET"),
            access_token=os.environ.get("MASTODON_ACCESS_TOKEN"),
            api_base_url=os.environ.get("MASTODON_API_BASE_URL"),
        )

        # Craft your toot. You can customize this message.
        toot = f"New blog post: {post_title}\n\nRead more here: {post_url}"
        mastodon.status_post(toot)
        return "Successfully shared to Mastodon!"
    except Exception as e:
        return f"Error sharing to Mastodon: {e}"


def share_to_bluesky(post_title, post_url):
    """
    Shares a blog post to BlueSky.
    """
    try:
        client = Client()
        client.login(
            os.environ.get("BLUESKY_HANDLE"), os.environ.get("BLUESKY_APP_PASSWORD")
        )

        # Craft your skeet. You can customize this message.
        post = f"New blog post: {post_title}\n\nRead more here: {post_url}"
        client.send_post(text=post)
        return "Successfully shared to BlueSky!"
    except Exception as e:
        return f"Error sharing to BlueSky: {e}"
