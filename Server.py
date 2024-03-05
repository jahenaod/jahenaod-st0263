# server.py
from flask import Flask, request, jsonify
import json
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

DATABASE_FILE = 'p2p_network.db'

if os.path.exists(DATABASE_FILE):
    os.remove(DATABASE_FILE)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_FILE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

DATABASE_FILE = 'sqlite:///p2p_network.db'

users = {}
files = {}
peers = {}

SERVER_IP = os.getenv('SERVER_URL', 'localhost')
SERVER_PORT = os.getenv('SERVER_PORT', '4001')

class Peer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False )
    ip = db.Column(db.String(15), nullable=False)
    port = db.Column(db.String(5), nullable=False)
    files = db.relationship('File', backref='peer', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    peer_id = db.Column(db.Integer, db.ForeignKey('peer.id'), nullable=False)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return "P2P File Sharing Server is running."

@app.route('/login', methods=['POST'])
def login(): #Con DB
    data = request.json
    username = data['username']
    password = data['password']
    ip = data['ip']
    port = data['port']
    # Asegúrate de que 'files' sea una lista vacía si no se proporciona
    files = data.get('files', [])

    peer = Peer.query.filter_by(username=username).first()
    if not peer:
        # Si el peer no existe, crear uno nuevo con una lista de archivos inicialmente vacía
        peer = Peer(username=username, ip=ip, port=port)
        db.session.add(peer)
    else:
        # Si el peer ya existe, actualiza su información
        peer.ip = ip
        peer.port = port
        # Opcional: aquí podrías manejar la actualización/remoción de archivos
    db.session.commit()

    return jsonify({"message": f"Peer {username} logged in successfully"}), 200

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    
    file_name = data['file_name']  # El nombre del archivo a subir
    file_url = data['url'] #URL del archivo 
    username = data['name_peer']  # Asume que el cliente envía su nombre de usuario

    # Buscar el peer por su nombre de usuario
    peer = Peer.query.filter_by(username=username).first()
    if not peer:
        return jsonify({"error": "Peer not found"}), 404

    # Verificar si el archivo ya existe para este peer
    existing_file = File.query.filter_by(username = username, file_name=file_name, url= file_url, peer_id=peer.id).first()
    if existing_file:
        return jsonify({"error": "File already exists"}), 400

    # Crear un nuevo registro de archivo y asociarlo con el peer
    new_file = File(username = username ,file_name=file_name, url= file_url, peer_id=peer.id)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": f"File {file_name} uploaded successfully"}), 200

@app.route('/listFiles', methods=['GET'])
def list_files():
    with app.app_context():
        all_files = File.query.all()
        files_list = []
        for file in all_files:
            file_data = {
                'id': file.id,
                'username': file.peer.username,
                'file_name': file.file_name,
                'file_url': file.url
            }
            files_list.append(file_data)
        return jsonify(files_list), 200

@app.route('/download', methods=['GET'])
def download():
    file_name = request.args.get('file_name')
    # Busca el archivo por su nombre
    file = File.query.filter_by(file_name=file_name).first()
    if file:
        # Si el archivo existe, devuelve la URL para descargarlo
        return jsonify({"file_url": file.url,
                        "Peer Owner": file.username }), 200
    else:
        # Si el archivo no se encuentra, devuelve un mensaje de error
        return jsonify({"message": "File not found"}), 404


@app.route('/listPeers', methods=['GET'])
def list_peers():
    all_peers = Peer.query.all()
    peers_list = []
    for peer in all_peers:
        peer_data = {
            'id': peer.id,
            'username': peer.username,
            'ip': peer.ip,
            'port': peer.port
        }
        peers_list.append(peer_data)
    return jsonify(peers_list), 200



if __name__ == "__main__":
    app.run(host=SERVER_IP, port=SERVER_PORT, debug=True)
