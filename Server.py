# server.py
from flask import Flask, request, jsonify
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)

users = {}
files = {}
peers = {}

SERVER_IP = os.getenv('SERVER_URL', 'localhost')

@app.route('/')
def index():
    return "P2P File Sharing Server is running."

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    ip = data['ip']
    port = data['port']
    peer_type = data.get('peer_type')
    peers[username] = {'ip': ip, 'port' : port}
    if username in users and users[username] != password:
        return jsonify({"message": "Invalid password"}), 403
    users[username] = password

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Conditional logic to load different .env files
    if peer_type == 'peer1':
        dotenv_path = os.path.join(script_dir, '.env-peer1')
    elif peer_type == 'peer2':
        dotenv_path = os.path.join(script_dir, '.env-Peer2')  # Adjust the case as necessary
    elif peer_type == 'peer3':
        dotenv_path = os.path.join(script_dir, '.env-peer3')
    else:
        # Handle unexpected peer_type or set a default .env file
        dotenv_path = os.path.join(script_dir, '.env-peer1')

    return jsonify({"message": f"User {username} logged in successfully"}), 200

import json

def update_files_db(file_name, file_url):
    db_path = 'files_db.json'
    files = {}
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            try:
                files = json.load(f)
            except json.JSONDecodeError:
                pass  # El archivo está vacío o corrupto, se iniciará como vacío.

    files[file_name] = file_url

    with open(db_path, 'w') as f:
        json.dump(files, f)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    file_name = data['file_name']
    file_url = data['url']
    name_peer = data['name_peer']
    files[file_name] = file_url
    peers[name_peer] = name_peer
    update_files_db(file_name, file_url, name_peer)  # Actualiza el archivo JSON
    return jsonify({"message": f"File {file_name} uploaded successfully"}), 200


@app.route('/download', methods=['GET'])
def download():
    file_name = request.args.get('file_name')
    if file_name in files:
        return jsonify({"file_url": files[file_name]}), 200
    return jsonify({"message": "File not found"}), 404

@app.route('/listPeers', methods=['GET'])
def list_peers():
    print(peers)
    return peers 


if __name__ == "__main__":
    app.run(host=SERVER_IP, port=4001, debug=True)
