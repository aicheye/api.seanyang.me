import json
import os

from flask import Flask, jsonify, request
import git
import sys
import requests
from config import Config

from rate_limiter import increment_and_check, get_count

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    cwd = os.getcwd()

    return jsonify({
        'git': {
            'branch': git.Repo(cwd).active_branch.name,
            'commit': git.Repo(cwd).head.commit.hexsha,
            'author': git.Repo(cwd).head.commit.author.name,
            'message': git.Repo(cwd).head.commit.message,
            'remote': next(git.Repo(cwd).remote().urls)
        },
        'python': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'status': 'ok',
        'service': 'api.seanyang.me'
    }), 200

@app.route('/cat', methods=['POST'])
def cat():
    # Enforce hourly global limit
    allowed, hr_count = increment_and_check('cat', Config.CAT_HOURLY_LIMIT)
    if not allowed:
        return jsonify({
            'status': 'error',
            'message': 'Hourly cat limit reached',
            'hourly_count': hr_count,
            'hourly_limit': Config.CAT_HOURLY_LIMIT
        }), 429

    # If allowed, increment total cat clicks
    clicks = 0

    # Load current count
    if not os.path.exists(Config.CAT_STORE_FILE):
        print("Creating cat store file")
        clicks = 0
    try:
        with open(Config.CAT_STORE_FILE, 'r') as f:
            clicks = json.load(f).get('count', 0)
    except Exception:
        # Corrupt or unreadable file — start fresh
        clicks = 0

    # Increment
    clicks += 1

    # Save updated count
    if not (os.path.exists(Config.CAT_STORE_FILE)):
        with open(Config.CAT_STORE_FILE, 'w') as f:
            json.dump({'count': 0}, f)

    tmp = Config.CAT_STORE_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump({'count': clicks}, f)
    # atomic replace
    os.replace(tmp, Config.CAT_STORE_FILE)

    return jsonify({
        'status': 'ok',
        'count': clicks,
        'hourly_count': hr_count,
        'hourly_limit': Config.CAT_HOURLY_LIMIT
    }), 200


@app.route('/poke', methods=['POST'])
def poke():
    data = request.get_json() or {}

    message = data.get('message') or 'Poke!'
    author = data.get('author') or 'Anonymous'

    if len(message) > 42:
        return jsonify({
            'status': 'error',
            'message': 'Message too long (max 42 characters)'
        }), 400

    if len(author) > 21:
        return jsonify({
            'status': 'error',
            'message': 'Author name too long (max 21 characters)'
        }), 400

    # Enforce hourly global limit for poke
    allowed, hr_count = increment_and_check('poke', Config.POKE_HOURLY_LIMIT)
    if not allowed:
        return jsonify({
            'status': 'error',
            'message': 'Hourly poke limit reached',
            'hourly_count': hr_count,
            'hourly_limit': Config.POKE_HOURLY_LIMIT
        }), 429

    response = requests.post(
        'https://api.pushover.net/1/messages.json',
        headers={
            'Content-Type': 'application/json',
        },
        json={
            'token': Config.PUSHOVER_API_TOKEN,
            'user': Config.PUSHOVER_USER_KEY,
            'message': f'{message} - {author}'
        }
    )

    if response.status_code != 200:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send notification'
        }), 500

    return jsonify({
        'status': 'ok',
        'message': 'Poke sent successfully',
        'hourly_count': hr_count,
        'hourly_limit': Config.POKE_HOURLY_LIMIT
    }), 200


if __name__ == '__main__':
    app.run()
