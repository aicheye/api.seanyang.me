import os

from dotenv import load_dotenv, find_dotenv

os.mkdir('.env') if not os.path.exists('.env') else None
load_dotenv(find_dotenv())


class Config:
    DEBUG: str = os.environ.get('DEBUG') or False
    TESTING: str = os.environ.get('TESTING') or False
    PUSHOVER_API_TOKEN: str = os.environ.get('PUSHOVER_API_TOKEN')
    PUSHOVER_USER_KEY: str = os.environ.get('PUSHOVER_USER_KEY')
    CAT_CLICKS: str = int(os.environ.get('CAT_CLICKS', 0))
