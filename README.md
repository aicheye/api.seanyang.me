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
