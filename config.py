import os

from dotenv import find_dotenv, dotenv_values

os.mknod('.env') if not os.path.exists('.env') else None
env = dotenv_values(find_dotenv() or '.env')

class Config:
    DEBUG: str = env.get('DEBUG') or False
    TESTING: str = env.get('TESTING') or False
    PUSHOVER_API_TOKEN: str = env.get('PUSHOVER_API_TOKEN')
    PUSHOVER_USER_KEY: str = env.get('PUSHOVER_USER_KEY')

    # Hourly rate limits (0 or negative -> unlimited). Configure via .env
    CAT_HOURLY_LIMIT = int(env.get('CAT_HOURLY_LIMIT', '100'))
    POKE_HOURLY_LIMIT = int(env.get('POKE_HOURLY_LIMIT', '60'))

    # Store files
    CAT_STORE_FILE = env.get('CAT_STORE_FILE', 'data/.cat_clicks.json')
    RATE_LIMIT_STORE_FILE = env.get('RATE_LIMIT_STORE_FILE', 'data/.rate_limits.json')
