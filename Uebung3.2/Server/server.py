import os
import socket
import json
import signal
import sys
import grpc
import threading
from concurrent import futures
from time import sleep

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Controller')))

import robot_controller_pb2
import robot_controller_pb2_grpc

data_store = {
    "robots": {},
    "current_captain": "Captain A",
    "controller_status": "Healthy",
    "dummy_data": ""
}

grpc_server_ready = threading.Event()

class RobotControllerServicer(robot_controller_pb2_grpc.RobotControllerServicer):
    def __init__(self, shared_data_store):
        self.data_store = shared_data_store

    def RegisterRobot(self, request, context):
        client_ip = context.peer()  # Get the client IP
        self.data_store["robots"][request.id] = {"ip": client_ip, "status": "Unknown"}
        print(f"Robot {request.id} with {client_ip} registered")
        # print(self.data_store)
        return robot_controller_pb2.RegistrationResponse(message="Robot registered")

    def SendStatus(self, request, context):
        if request.id in self.data_store["robots"]:
            self.data_store["robots"][request.id]["status"] = request.status
            print(f"Status updated for robot {request.id} is {request.status}")
            return robot_controller_pb2.StatusResponse(message="Status updated")
        else:
            return robot_controller_pb2.StatusResponse(message="Robot not registered")

    def ElectCaptain(self, request, context):
        new_captain = "Captain A" if data_store["current_captain"] == "Captain B" else "Captain B"
        self.data_store["current_captain"] = new_captain
        print(f"New captain elected: {new_captain}")
        return robot_controller_pb2.CaptainResponse(new_captain=new_captain)
    
    def UnregisterRobot(self, request, context):
        if request.id in self.data_store["robots"]:
            del self.data_store["robots"][request.id]
            client_ip = context.peer()  # Get the client IP
            print(f"Robot {request.id} with {client_ip} unregistered")
            # print(self.data_store)
            return robot_controller_pb2.RegistrationResponse(message="Robot unregistered")
        else:
            return robot_controller_pb2.RegistrationResponse(message="Robot not registered")

def serve():
    """Start gRPC server and set the ready flag."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    robot_controller_pb2_grpc.add_RobotControllerServicer_to_server(RobotControllerServicer(data_store), server)
    server.add_insecure_port('[::]:50051')
    
    server.start()
    grpc_server_ready.set()
    print("✅ gRPC server started on port 50051")
    
    server.wait_for_termination()

def start_http_server():
    """Start HTTP server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 8080
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)

    print("✅ HTTP server running on port 8080")   

    while True:
        try:
            client_socket, _ = server_socket.accept()
            handle_request(client_socket)
        except Exception as e:
            print(f"⚠️ HTTP Server Error: {e}")

def handle_request(client_socket):
    """Handle incoming HTTP requests."""
    request = client_socket.recv(1024).decode('utf-8')
    response = handle_http_request(request)
    client_socket.sendall(response.encode('utf-8'))
    client_socket.close()

def handle_http_request(request):
    """Process HTTP requests and generate responses."""
    headers = request.split('\r\n')
    method, path = headers[0].split(' ')[:2]

    if method == 'GET':
        return handle_get_request(path)
    elif method == 'POST':
        return handle_post_request(headers, request)
    else:
        return "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

def handle_get_request(path):
    """Handle different GET routes."""
    if path == "/":
        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nServer is running"
    elif path == "/status":
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{json.dumps(data_store)}"
    elif path == "/captain":
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{json.dumps({'captain': data_store['current_captain']})}"
    elif path == "/health":
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nController is {data_store['controller_status']}"
    elif path == "/server_status":
        if grpc_server_ready.is_set():
            return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\ngRPC Server is UP"
        else:
            return "HTTP/1.1 503 Service Unavailable\r\nContent-Type: text/plain\r\n\r\ngRPC Server is DOWN"
    else:
        return "HTTP/1.1 404 Not Found\r\n\r\n"

def handle_post_request(headers, request):
    """Handle incoming POST requests."""
    content_length = int([header for header in headers if "Content-Length" in header][0].split(':')[1].strip())
    body = request.split('\r\n\r\n')[1][:content_length]
    data_store["dummy_data"] = body
    return "HTTP/1.1 200 OK\r\n\r\nData received and stored"

def signal_handler(sig, frame):
    """Gracefully shutdown the HTTP server."""
    print('\nServer Gracefully shutting down servers...')
    sys.exit(0)

if __name__ == "__main__":
    # ✅ Register signal handler in the MAIN THREAD
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    grpc_thread = threading.Thread(target=serve, daemon=True)
    grpc_thread.start()

    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    while True:
        sleep(1)
