**Api.Seanyang.Me**

- **Description:** Small Flask-based API used by seanyang.me for lightweight utilities (cat click counter, poke notifications, and health/git info).
- **Service file:** `app.py` (Flask app exposing endpoints)

**Features**
- **Status:** `GET /` — returns git and runtime info (commit, branch, Python version, timestamp).
- **Health Check**: `GET /health` — returns health status.
- **Cat counter:** `POST /cat` — increments a persistent cat click counter stored in `data/.cat_clicks.json`. Enforces an hourly global limit.
- **Poke:** `POST /poke` — sends a Pushover notification. Accepts JSON with `message` and optional `author`. Enforces an hourly global limit.

**Requirements**
- Python packages (install via `pip install -r requirements.txt`): `Flask`, `flask-cors`, `GitPython`, `requests`, `python-dotenv`, `gunicorn`.

**Quickstart (local)**
- Create and activate a virtual environment (recommended):

```
python -m venv .venv
source .venv/bin/activate
```

- Install dependencies:

```
pip install -r requirements.txt
```

- Ensure the `data/` directory exists and is writable by the process:

```
mkdir -p data
```

- Create a `.env` file at the project root (an empty one is OK — `config.py` will create it if missing). Example `.env` values:

```
# .env example
PUSHOVER_API_TOKEN=your_pushover_api_token_here
PUSHOVER_USER_KEY=your_pushover_user_key_here
CAT_HOURLY_LIMIT=100
POKE_HOURLY_LIMIT=60
CAT_STORE_FILE=data/.cat_clicks.json
RATE_LIMIT_STORE_FILE=data/.rate_limits.json
DEBUG=False
TESTING=False
```

- Run the app for development:

```
python app.py
```

- Run with Gunicorn for production (example):

```
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**API Usage Examples**
- Health / service info:

```
curl -s http://localhost:5000/ | jq
```

- Increment cat counter:

```
curl -X POST http://localhost:5000/cat
```

- Send a poke (Pushover):

```
curl -X POST http://localhost:5000/poke \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hello","author": "Alice"}'
```

Notes:
- `POST /cat` and `POST /poke` return HTTP `429` when the hourly global limit (configured in `.env`) is reached.
- `POST /poke` enforces max lengths: `message` max 42 characters, `author` max 21 characters.
- The app stores counters and rate-limit state in files configured by `Config` (see `config.py`). Ensure those paths are writable.

**Configuration**
- Configuration is loaded from a `.env` file via `python-dotenv`. The main configuration class is `Config` in `config.py`.
- Key environment variables:
  - `PUSHOVER_API_TOKEN` — API token for Pushover (required for `poke`).
  - `PUSHOVER_USER_KEY` — Pushover user key (required for `poke`).
  - `CAT_HOURLY_LIMIT`, `POKE_HOURLY_LIMIT` — hourly global limits (integers, `0` or negative -> unlimited).
  - `CAT_STORE_FILE`, `RATE_LIMIT_STORE_FILE` — filesystem paths for persisted stores.

**Development & Tests**
- There are no automated tests included. To exercise endpoints locally, use the `requests/` http snippets (`requests/cat.http`, `requests/poke.http`) or the `curl` examples above.

**Troubleshooting**
- If the service cannot write counts or rate-limit data, check permissions on `data/` and the paths configured in `.env`.
- If Pushover requests fail, verify `PUSHOVER_API_TOKEN` and `PUSHOVER_USER_KEY` are correct and that outbound HTTPS is allowed.

**Files of interest**
- `app.py` — Flask application and endpoints
- `config.py` — environment-backed configuration
- `rate_limiter.py` — simple filesystem-backed hourly rate limiting
- `data/` — persistent JSON files used by the app
- `requests/` — example HTTP requests

If you'd like, I can add a `Dockerfile`, a `systemd` service unit example, or a minimal CI job to run basic smoke checks. Want one of those next?
# api.seanyang.me

This is a simple Flask API that provides a few micro-services.

## Endpoints

*   `GET /`: Returns the application's status, including git information and Python version.
*   `POST /cat`: Increments a counter for cat clicks. This endpoint is rate-limited.
*   `POST /poke`: Sends a push notification via Pushover. This endpoint is also rate-limited.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure environment variables:**
    Create a `.env` file in the root of the project and add the following variables:
    ```
    PUSHOVER_API_TOKEN=your_pushover_api_token
    PUSHOVER_USER_KEY=your_pushover_user_key
    ```

## Running the application

### Development

```bash
python app.py
```

### Production

It's recommended to use a WSGI server like Gunicorn:

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```
