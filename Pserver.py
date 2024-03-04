# pserver.py
from concurrent import futures
import socket
import grpc
import p2p_pb2
import p2p_pb2_grpc
from flask import Flask
import time
import dotenv
import json
from Server import db, File, Peer
from flask_sqlalchemy import SQLAlchemy
import requests

#app = Flask(__name__)
files = {}

import json
import os

#DATABASE_FILE = 'p2p_network.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_FILE
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)

DATABASE_FILE = 'sqlite:///p2p_network.db'

GRCP_SERVER_IP = os.getenv('GRCP_SERVER_URL', 'localhost')
GRCP_SERVER_PORT1 = os.getenv('GRCP_SERVER_PORT', '5001')

class FileService(p2p_pb2_grpc.FileServiceServicer):
    def DownloadFile(self, request, context):
        db_path = 'files_db.json'
        file_name = request.file_name
        files = {}
        
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                try:
                    files = json.load(f)
                except json.JSONDecodeError:
                    pass  # El archivo está vacío o corrupto, se manejará como vacío.

        file_url = files.get(file_name)
        if file_url:
            return p2p_pb2.DownloadResponse(file_url=file_url)
        else:
            context.abort(grpc.StatusCode.NOT_FOUND, "File not found")
    
    def ListFiles(self, request, context):
        # URL del endpoint de Flask
        flask_endpoint = 'http://localhost:4001/listFiles'
        try:
            # Realizar la petición GET al servidor Flask
            response = requests.get(flask_endpoint)
            # Asegúrate de que la petición fue exitosa
            if response.status_code == 200:
                files_data = response.json()  # Asume que el endpoint devuelve una lista de archivos en formato JSON
                # Convertir los datos JSON a objetos FileInfo
                files_info = [
                    p2p_pb2.FileInfo(
                        file_name=file['file_name'],
                        file_url=file['file_url'],
                        peer_name=file['username']
                    ) for file in files_data
                ]
                # Devolver la respuesta con la lista de archivos
                return p2p_pb2.ListFilesResponse(files=files_info)
            else:
                context.abort(grpc.StatusCode.INTERNAL, 'Error interno al obtener la lista de archivos')
        except Exception as e:
            # Manejo de excepciones, como problemas de red o errores de decodificación JSON
            context.abort(grpc.StatusCode.INTERNAL, f'Error al realizar la petición: {str(e)}')

def check_port_available(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) != 0

def find_free_port(start_port):
    port = start_port
    while not check_port_available(GRCP_SERVER_IP, port):
        port += 1
    return port

def serve_grpc():
    server_port = find_free_port(int(GRCP_SERVER_PORT1))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p2p_pb2_grpc.add_FileServiceServicer_to_server(FileService(), server)
    server.add_insecure_port(f"{GRCP_SERVER_IP}:{server_port}")
    print(f"Starting gRPC server on {GRCP_SERVER_IP}:{server_port}")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

def start_peer_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Listening on {host}:{port}...")
    conn, addr = server_socket.accept()
    print(f"Connection from {addr} has been established!")
    
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print("Received:", data.decode())
        conn.sendall(data)
    conn.close()

# Ejemplo de uso
# start_peer_server('0.0.0.0', 5002)



if __name__ == '__main__':
    print("P2P File Sharing Server is running.")
    serve_grpc()
