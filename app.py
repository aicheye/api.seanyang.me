"""api.seanyang.me small Flask API.

Provides endpoints used on seanyang.me for simple utilities
like counting cat clicks and sending poke notifications.
"""

import json
import os
import sys

from datetime import datetime, timezone
from flask import Flask, jsonify, request  # pylint: disable=import-error
from flask_cors import CORS  # pylint: disable=import-error
import git  # pylint: disable=import-error
import requests

from config import Config
from rate_limiter import increment_and_check

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": ["https://seanyang.me", "https://www.seanyang.me"]}},
)


@app.route("/", methods=["GET"])
def main():
    """Return basic service and git info for the running app."""
    cwd = os.getcwd()

    return jsonify(
        {
            "git": {
                "author": git.Repo(cwd).head.commit.author.name,
                "branch": git.Repo(cwd).active_branch.name,
                "commit": git.Repo(cwd).head.commit.hexsha,
                "message": git.Repo(cwd).head.commit.message.strip(),
                "remote": next(git.Repo(cwd).remote().urls),
            },
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "service": "api.seanyang.me",
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }
    ), 200


@app.route("/cat", methods=["POST"])
def cat():
    """Increment and return the persistent cat click counter.

    Enforces hourly global limit via `increment_and_check`.
    """
    # Enforce hourly global limit
    allowed, hr_count = increment_and_check("cat", Config.CAT_HOURLY_LIMIT)
    if not allowed:
        return jsonify(
            {
                "status": "error",
                "message": "Hourly cat limit reached",
                "hourly_count": hr_count,
                "hourly_limit": Config.CAT_HOURLY_LIMIT,
            }
        ), 429

    # If allowed, increment total cat clicks
    clicks = 0

    # Load current count
    if not os.path.exists(Config.CAT_STORE_FILE):
        print("Creating cat store file")
        clicks = 0
    try:
        with open(Config.CAT_STORE_FILE, "r", encoding="utf-8") as f:
            clicks = json.load(f).get("count", 0)
    except (json.JSONDecodeError, OSError):
        # Corrupt or unreadable file — start fresh
        clicks = 0

    # Increment
    clicks += 1

    # Save updated count
    if not os.path.exists(Config.CAT_STORE_FILE):
        with open(Config.CAT_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"count": 0}, f)

    tmp = Config.CAT_STORE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"count": clicks}, f)
    # atomic replace
    os.replace(tmp, Config.CAT_STORE_FILE)

    return jsonify(
        {
            "status": "ok",
            "count": clicks,
            "hourly_count": hr_count,
            "hourly_limit": Config.CAT_HOURLY_LIMIT,
        }
    ), 200


@app.route("/poke", methods=["POST"])
def poke():
    """Send a poke notification via Pushover with basic validation."""
    data = request.get_json() or {}

    message = data.get("message") or "Poke!"
    author = data.get("author") or "Anonymous"

    if len(message) > 42:
        return jsonify(
            {"status": "error", "message": "Message too long (max 42 characters)"}
        ), 400

    if len(author) > 21:
        return jsonify(
            {"status": "error", "message": "Author name too long (max 21 characters)"}
        ), 400

    # Enforce hourly global limit for poke
    allowed, hr_count = increment_and_check("poke", Config.POKE_HOURLY_LIMIT)
    if not allowed:
        return jsonify(
            {
                "status": "error",
                "message": "Hourly poke limit reached",
                "hourly_count": hr_count,
                "hourly_limit": Config.POKE_HOURLY_LIMIT,
            }
        ), 429

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "token": Config.PUSHOVER_API_TOKEN,
            "user": Config.PUSHOVER_USER_KEY,
            "message": f"{message} - {author}",
        },
        timeout=5,
    )

    if response.status_code != 200:
        return jsonify(
            {"status": "error", "message": "Failed to send notification"}
        ), 500

    return jsonify(
        {
            "status": "ok",
            "message": "Poke sent successfully",
            "hourly_count": hr_count,
            "hourly_limit": Config.POKE_HOURLY_LIMIT,
        }
    ), 200


if __name__ == "__main__":
    app.run()
