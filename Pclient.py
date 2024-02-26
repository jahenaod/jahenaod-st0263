# pClient.py
import grpc
import requests
import p2p_pb2
import p2p_pb2_grpc

def download_file_grpc(file_name):
    with grpc.insecure_channel('localhost:5001') as channel:
        stub = p2p_pb2_grpc.FileServiceStub(channel)
        try:
            response = stub.DownloadFile(p2p_pb2.DownloadRequest(file_name=file_name))
            print(f"File URL: {response.file_url}")
        except grpc.RpcError as e:
            print(f"gRPC error: {e.details()}")

def upload_file(file_name, file_url):
    response = requests.post('http://localhost:4001/upload', json={'file_name': file_name, 'url': file_url})
    print(response.json()['message'])

if __name__ == "__main__":
    while True:
        print("\nWhat do you want to do?")
        print("1. Download file with gRPC")
        print("2. Upload file with HTTP")
        print("3. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            file_name = input("Enter file name to download: ")
            download_file_grpc(file_name)
        elif choice == "2":
            file_name = input("Enter file name to upload: ")
            file_url = input("Enter file URL: ")
            upload_file(file_name, file_url)
        elif choice == "3":
            break
