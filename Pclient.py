# pClient.py
import grpc
import requests
import p2p_pb2
import p2p_pb2_grpc
import os
import dotenv

SERVER_IP = os.getenv('SERVER_URL', 'localhost')
SERVER_PORT = os.getenv('SERVER_PORT', '4001')
GRCP_SERVER_IP = os.getenv('GRCP_SERVER_URL', 'localhost')
GRCP_SERVER_PORT1 = os.getenv('GRCP_SERVER_PORT', '5001')


def login_peer():
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")
        ip = input("Enter ip address: ")
        port = input("Enter port: ")
        peerType= input("Do you want to be peer1, peer2 or peer3 ? : ")
        pclient_data = {"username": username, "password": password, "ip": ip, "port": port, "peerType": peerType}
        
        response = requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/login", json=pclient_data)
        
        if response.status_code == 200:
            print(f"Logged in as {username}")
            break
        else:
            print("Invalid credentials. Please try again.")
            response = login_peer(pclient_data)
        print(f"Logged in as {username}")


def download_file_grpc(file_name):
    with grpc.insecure_channel(f'{GRCP_SERVER_IP}:{GRCP_SERVER_PORT1}') as channel:
        stub = p2p_pb2_grpc.FileServiceStub(channel)
        try:
            response = stub.DownloadFile(p2p_pb2.DownloadRequest(file_name=file_name))
            print(f"File URL: {response.file_url}")
        except grpc.RpcError as e:
            print(f"gRPC error: {e.details()}")

def upload_file(file_name, file_url, name_peer):
    response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/upload', json={'file_name': file_name, 'url': file_url, 'name_peer': name_peer})
    print(response.json()['message'])

def list_peers():
    response = requests.get(f"http://{SERVER_IP}:{SERVER_PORT}/listPeers")
    print(response.json())

def list_files_grcp():
  with grpc.insecure_channel(f'{GRCP_SERVER_IP}:{GRCP_SERVER_PORT1}') as channel:
        stub = p2p_pb2_grpc.FileServiceStub(channel)
        try:
            # Enviar una solicitud vacía de ListFilesRequest
            response = stub.ListFiles(p2p_pb2.ListFilesRequest())
            # Procesar la respuesta
            for file_info in response.files:
                print(f"File Name: {file_info.file_name}, URL: {file_info.file_url}, Peer Name: {file_info.peer_name}")
        except grpc.RpcError as e:
            print(f"gRPC error: {e.details()}")

if __name__ == "__main__":
    login_peer()
    while True:
        print("\nWhat do you want to do?")
        print("1. Download file with gRPC")
        print("2. Upload file with HTTP")
        print("3. List peers")
        print("4. List file")
        print("5. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            file_name = input("Enter file name to download: ")
            download_file_grpc(file_name)
        elif choice == "2":
            file_name = input("Enter file name to upload: ")
            file_url = input("Enter file URL: ")
            name_peer = input("Enter peer name or number: ")
            upload_file(file_name, file_url, name_peer)
        elif choice == "3":
            list_peers() 
        elif choice == "4":
            list_files_grcp()
        elif choice == "5":
            break
