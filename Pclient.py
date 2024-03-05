# pClient.py
import grpc
import requests
import p2p_pb2
import p2p_pb2_grpc
import os
import dotenv
import socket

SERVER_IP = os.getenv('SERVER_URL', 'localhost')
SERVER_PORT = os.getenv('SERVER_PORT', '4001')
GRCP_SERVER_IP = os.getenv('GRCP_SERVER_URL', 'localhost')
GRCP_SERVER_PORT1 = os.getenv('GRCP_SERVER_PORT', '5001')


def login_peer():
    while True:
        choice = input("Do you want connect to a peer or to a server?")
        if choice == "peer":
            list_peers()
            username = input("Which username do you want to connect to? ")
            host = input("Enter peer's IP address: ")
            port = input("Enter peer's port: ")
            connect_to_peer(host, int(port))
            break

        elif choice == "server":
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

        else:
            print("Please enter a valid option ('peer' or 'server').")

def download_file_grpc(file_name):
    # Crea un canal de comunicación con el servidor gRPC
    with grpc.insecure_channel(f"{GRCP_SERVER_IP}:{GRCP_SERVER_PORT1}") as channel:
        # Crea un stub basado en el canal
        stub = p2p_pb2_grpc.FileServiceStub(channel)
        
        # Crea el objeto de solicitud con el nombre del archivo
        request = p2p_pb2.DownloadRequest(file_name=file_name)
        
        try:
            # Realiza la llamada al método DownloadFile del servicio
            response = stub.DownloadFile(request)
            # Imprime la URL del archivo obtenida en la respuesta
            print(f"File URL: {response.file_url}")
            print(f"Peer Owner: {response.peer_owner}")
        except grpc.RpcError as e:
            print(f"Error al descargar el archivo: {e.details()}")


def upload_file(file_name, file_url, name_peer):
    response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/upload', json={'file_name': file_name, 'url': file_url, 'name_peer': name_peer})
    response_data = response.json()
    # Verificar si 'message' está en la respuesta, manejar si no lo está
    if 'message' in response_data:
        print(response_data['message'])
    else:
        # Imprimir la respuesta completa para depuración si 'message' no se encuentra
        print("Response did not contain 'message'. Full response:", response_data)

def list_peers():
    response = requests.get(f"http://{SERVER_IP}:{SERVER_PORT}/listPeers")
    if response.status_code == 200:
        peers_list = response.json()
        for peer in peers_list:
            print(f"Username: {peer['username']}, IP: {peer['ip']}, Port: {peer['port']}")
    else:
        print(f"Error al listar peers: {response.status_code}")
        
def list_files_grcp():
  with grpc.insecure_channel(f'{GRCP_SERVER_IP}:{GRCP_SERVER_PORT1}') as channel:
        stub = p2p_pb2_grpc.FileServiceStub(channel)
        try:
            # Enviar una solicitud vacía de ListFilesRequest
            response = stub.ListFiles(p2p_pb2.ListFilesRequest())
            # Procesar la respuesta
            for file_info in response.files:
                print(f"File Name: {file_info.file_name}, URL: {file_info.file_url}, Username: {file_info.peer_name}")
        except grpc.RpcError as e:
            print(f"gRPC error: {e.details()}")

def connect_to_peer(host, port):
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
        client_socket.connect((host, int(port)))
        received_data = client_socket.recv(1024)
        try:
            # Intenta decodificar como UTF-8, reemplazando caracteres no decodificables
            print("Received:", received_data.decode('utf-8', 'replace'))
        except UnicodeDecodeError:
            # Manejo alternativo si aún así se encuentra un error
            print("Received data could not be decoded as UTF-8.")
  finally:
        client_socket.close()

# Ejemplo de uso
# connect_to_peer('127.0.0.1', 5002, "Hello, peer!")

if __name__ == "__main__":
    login_peer()
    while True:
        print("\nWhat do you want to do?")
        print("1. Download file with gRPC")
        print("2. Upload file with HTTP")
        print("3. List peers")
        print("4. List file")
        print("5. exit")
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
