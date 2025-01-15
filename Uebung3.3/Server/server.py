import os
import re
import socket
import json
import signal
import sys
import grpc
import threading
import stomp
from concurrent import futures
from time import sleep

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Controller')))

import robot_controller_pb2
import robot_controller_pb2_grpc
import traceback

data_store = {
    "robots": {},
    "current_captain": "Captain A",
    "controller_status": "Healthy",
    "dummy_data": ""
}

grpc_server_ready = threading.Event()

targetBroker = os.getenv("TARGET_SERVER", "localhost")

connection = stomp.Connection([(targetBroker, 61613)])

def extract_ip(peer_address):
        """Extracts a clean IP (IPv4 or IPv6) from gRPC context.peer()."""
        if 'ipv6:%5B::1%5D' in peer_address: 
            return '::1'  # IPv6 localhost
        match = re.search(r'ipv[46]:\[(.*?)\]|\bipv[46]:(\S+):', peer_address)
        if match:
            return match.group(1) if match.group(1) else match.group(2)  # Extract the matched IP part
        return "Unknown"

class RobotControllerServicer(robot_controller_pb2_grpc.RobotControllerServicer):
    def __init__(self, shared_data_store):
        self.data_store = shared_data_store

    def RegisterRobot(self, request, context):
        client_ip = context.peer()  # Get the client IP
        self.data_store["robots"][request.id] = {"ip": client_ip, "status": "Unknown"}
        print(f"Robot {request.id} with {client_ip} registered")
        return robot_controller_pb2.RegistrationResponse(message="Robot registered")

    def SendStatus(self, request, context):
        if request.id in self.data_store["robots"]:
            self.data_store["robots"][request.id]["status"] = request.status
            print(f"Status updated for: {request.id} is {request.status}")
            
            additional_info = ""  # Ensure the variable is always defined
            if request.status == "Error" or request.status == "error":
                additional_info = f" {request.id} is unavailable. Election will be started!"
                election_command(additional_info=additional_info)

            info = "Status updated" + additional_info  # Simplified concatenation
            
            return robot_controller_pb2.StatusResponse(message=info)
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
            
            election_command(additional_info=f" robot {request.id} unregistered, election will be started!")
            additional_info = ", election will be started!"
            
            return robot_controller_pb2.RegistrationResponse(message="Robot unregistered" + additional_info)
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
    elif path == "/election": 
        election_command(additional_info=" User watns election. Election started!")
        return "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nElection command sent to the robots!"
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
    # Return a 404 Not Found response for unsupported paths
    else:
        return "HTTP/1.1 404 Bad Request\r\nContent-Type: text/plain\r\n\r\nNot Found"

def handle_post_request(headers, request):
    """Handle incoming POST requests."""
    content_length = int([header for header in headers if "Content-Length" in header][0].split(':')[1].strip())
    body = request.split('\r\n\r\n')[1][:content_length]
    data_store["dummy_data"] = body
    return "HTTP/1.1 200 OK\r\n\r\nData received and stored"

def signal_handler(sig, frame):
    """Gracefully shutdown the HTTP server."""
    connection.disconnect()
    print('\nServer Gracefully shutting down servers...')
    sys.exit(0)

def election_command(additional_info=""):
    for _, _ in data_store["robots"].items():
        connection.send(body='Attention all Robots!!' + additional_info, destination='/queue/robot_commands')

if __name__ == "__main__":
    # ✅ Register signal handler in the MAIN THREAD
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    sleep(1)

    connection.connect('username', 'password', wait=True)
    print("✅ STOMP connection established")

    grpc_thread = threading.Thread(target=serve, daemon=True)
    grpc_thread.start()

    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    while True:
        sleep(1)
