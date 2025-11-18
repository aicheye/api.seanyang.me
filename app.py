import os

from flask import Flask, jsonify, request
import git
import sys
import requests
from config import Config
from dotenv import find_dotenv, set_key

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    cwd = os.getcwd()

    return jsonify({})

    return jsonify({
        'git': {
            'branch': git.Repo(cwd).active_branch.name,
            'commit': git.Repo(cwd).head.commit.hexsha,
            'author': git.Repo(cwd).head.commit.author.name,
            'message': git.Repo(cwd).head.commit.message,
            'remote_url': next(git.Repo(cwd).remote().urls)
        },
        'python': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'status': 'ok',
        'service': 'api.seanyang.me'
    }), 200


@app.route('/cat', methods=['POST'])
def cat():
    Config.CAT_CLICKS += 1
    set_key(find_dotenv(), 'CAT_CLICKS', str(Config.CAT_CLICKS))
    return jsonify({
        'status': 'ok',
        'count': Config.CAT_CLICKS
    }), 200


@app.route('/poke', methods=['POST'])
def poke():
    data = request.get_json()

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
        'message': 'Poke sent successfully'
    }), 200


if __name__ == '__main__':
    app.run()
