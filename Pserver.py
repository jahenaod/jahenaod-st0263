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

app = Flask(__name__)
files = {}

import json
import os

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

def ListFiles(self, request, context):
        db_path = 'files_db.json'
        files_info = []
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                try:
                    files = json.load(f)
                    for file_name, info in files.items():
                        if isinstance(info, dict):  # Asegurarse de que info es un diccionario
                            files_info.append(p2p_pb2.FileInfo(
                                file_name=file_name,
                                file_url=info.get('url', ''),
                                peer_name=info.get('peer', '')
                            ))
                except json.JSONDecodeError:
                    context.abort(grpc.StatusCode.INTERNAL, "Internal server error")
        return p2p_pb2.ListFilesResponse(files=files_info)

if __name__ == '__main__':
    print("P2P File Sharing Server is running.")
    serve_grpc()
