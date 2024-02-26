# server.py
from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

users = {}
files = {}


@app.route('/')
def index():
    return "P2P File Sharing Server is running."

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    if username in users and users[username] != password:
        return jsonify({"message": "Invalid password"}), 403
    users[username] = password
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
    files[file_name] = file_url
    update_files_db(file_name, file_url)  # Actualiza el archivo JSON
    return jsonify({"message": f"File {file_name} uploaded successfully"}), 200


@app.route('/download', methods=['GET'])
def download():
    file_name = request.args.get('file_name')
    if file_name in files:
        return jsonify({"file_url": files[file_name]}), 200
    return jsonify({"message": "File not found"}), 404

if __name__ == "__main__":
    app.run(host='localhost', port=4001, debug=True)
