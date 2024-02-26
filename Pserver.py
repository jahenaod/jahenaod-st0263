# pserver.py
from concurrent import futures
import grpc
import p2p_pb2
import p2p_pb2_grpc
from flask import Flask
import time

app = Flask(__name__)
files = {}

import json
import os

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


def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p2p_pb2_grpc.add_FileServiceServicer_to_server(FileService(), server)
    server.add_insecure_port('localhost:5001')
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    print("P2P File Sharing Server is running.")
    serve_grpc()
