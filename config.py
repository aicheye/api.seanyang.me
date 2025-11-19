"""Configuration loader for the service.

Loads values from a `.env` file (created if missing) and exposes
configuration constants via the `Config` class.
"""

import os

from dotenv import find_dotenv, dotenv_values  # pylint: disable=import-error

# Ensure a .env file exists so dotenv_values has somewhere to read from.
if not os.path.exists(".env"):
    with open(".env", "a", encoding="utf-8"):
        pass

env = dotenv_values(find_dotenv() or ".env")


class Config:
    """Application configuration namespace.

    Attributes are uppercase to make them easy to discover and
    usable as constants throughout the app.
    """

    DEBUG: str = env.get("DEBUG") or False
    TESTING: str = env.get("TESTING") or False
    PUSHOVER_API_TOKEN: str = env.get("PUSHOVER_API_TOKEN")
    PUSHOVER_USER_KEY: str = env.get("PUSHOVER_USER_KEY")

    # Hourly rate limits (0 or negative -> unlimited). Configure via .env
    CAT_HOURLY_LIMIT = int(env.get("CAT_HOURLY_LIMIT", "100"))
    POKE_HOURLY_LIMIT = int(env.get("POKE_HOURLY_LIMIT", "60"))

    # Store files
    CAT_STORE_FILE = env.get("CAT_STORE_FILE", "data/.cat_clicks.json")
    RATE_LIMIT_STORE_FILE = env.get("RATE_LIMIT_STORE_FILE", "data/.rate_limits.json")

    @classmethod
    def as_dict(cls):
        """Return the uppercase config values as a dict for debugging."""
        return {k: getattr(cls, k) for k in dir(cls) if k.isupper()}

    @classmethod
    def get(cls, key, default=None):
        """Return a single config value by uppercase key or `default` if missing."""
        return getattr(cls, key, default)
