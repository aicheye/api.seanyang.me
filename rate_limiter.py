"""File-backed per-hour global rate limiter.

Stores a JSON object: {"hour": <int hour_key>, "counts": {"cat": n, "poke": m}}.
The hour key is timestamp // 3600 so it rotates every hour.
"""

import json
import os
import threading
import time

STORE_FILE = os.getenv("RATE_LIMIT_STORE_FILE", "data/.rate_limits.json")

_lock = threading.Lock()


def _hour_key(ts=None):
    if ts is None:
        ts = time.time()
    return int(ts // 3600)


def _load_state():
    if not os.path.exists(STORE_FILE):
        return {"hour": _hour_key(), "counts": {}}
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # If it's a different hour, reset counts
        if data.get("hour") != _hour_key():
            return {"hour": _hour_key(), "counts": {}}
        # ensure structure
        return {"hour": data.get("hour", _hour_key()), "counts": data.get("counts", {})}
    except (json.JSONDecodeError, OSError):
        # Corrupt or unreadable file — start fresh
        return {"hour": _hour_key(), "counts": {}}


def _save_state(state):
    tmp = STORE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f)
    # atomic replace
    os.replace(tmp, STORE_FILE)


def increment_and_check(endpoint: str, limit: int):
    """Increment the counter for `endpoint` and check against `limit`.

    Args:
        endpoint: a string key, e.g. 'cat' or 'poke'
        limit: integer hourly limit. If <= 0, treated as unlimited.

    Returns:
        (allowed: bool, count_after: int)
    """
    # Unlimited
    if not isinstance(limit, int) or limit <= 0:
        with _lock:
            state = _load_state()
            counts = state.setdefault("counts", {})
            counts[endpoint] = counts.get(endpoint, 0) + 1
            state["hour"] = _hour_key()
            _save_state(state)
            return True, counts[endpoint]

    with _lock:
        state = _load_state()
        # If hour rolled over, reset
        if state.get("hour") != _hour_key():
            state = {"hour": _hour_key(), "counts": {}}
        counts = state.setdefault("counts", {})
        current = counts.get(endpoint, 0)
        if current + 1 > limit:
            return False, current
        counts[endpoint] = current + 1
        state["counts"] = counts
        state["hour"] = _hour_key()
        _save_state(state)
        return True, counts[endpoint]


def get_count(endpoint: str):
    """Return current count for endpoint in this hour (no increment)."""
    state = _load_state()
    return state.get("counts", {}).get(endpoint, 0)
