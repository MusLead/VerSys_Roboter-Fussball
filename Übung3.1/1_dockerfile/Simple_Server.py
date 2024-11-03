import socket
import json
import time
import statistics
import signal
import sys

# Data storage dictionary
data_store = {
    "robots_active": 5,
    "current_captain": "Captain A",
    "controller_status": "Healthy",
    "dummy_data": ""
}

# Function to start the HTTP server
def start_server():
    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8080))  # Bind the socket to port 8080
    server_socket.listen(5)  # Listen for incoming connections
    print("HTTP server running on port 8080")

    def signal_handler(sig, frame):
        print('Gracefully shutting down the server...')
        server_socket.close()  # Close the server socket
        sys.exit(0)  # Exit the program

    # Register the signal handler for SIGINT (Ctrl + C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        try:
            client_socket, client_address = server_socket.accept()  # Accept a new connection
            handle_request(client_socket)  # Handle the client's request
        except Exception as e:
            print(f"Error: {e}")


# Function to handle incoming client requests
def handle_request(client_socket):
    # Receive the client's request
    request = client_socket.recv(1024).decode('utf-8')
    # Generate an appropriate response
    response = handle_http_request(request)
    # Send the response to the client
    client_socket.sendall(response.encode('utf-8'))
    # Close the client connection
    client_socket.close()

# Function to process the HTTP request and generate a response
def handle_http_request(request):
    # Split the request into lines
    headers = request.split('\r\n')
    # Extract the method and path from the request line
    method, path = headers[0].split(' ')[:2]

    # Handle GET requests
    if method == 'GET':
        return handle_get_request(path)
    # Handle POST requests
    elif method == 'POST':
        return handle_post_request(headers, request)
    # Return an error response for unsupported methods
    else:
        return "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

# Function to handle GET requests
def handle_get_request(path):
    # Return the status of the entire system
    if path == "/":
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{json.dumps({'Status': 'OK', 'Server': 'Running'})}"
    elif path == "/status":
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{json.dumps(data_store)}"
    # Return the current captain
    elif path == "/captain":
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{json.dumps({'captain': data_store['current_captain']})}"
    # Return the controller's status
    elif path == "/health":
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nController is {data_store['controller_status']}"
    # Initiate a new captain election
    elif path == "/election":
        data_store['current_captain'] = "Captain B"
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nNew captain elected: {data_store['current_captain']}"
    # Return a 404 Not Found response for unsupported paths
    else:
        return "HTTP/1.1 404 Not Found\r\n\r\n"

# Function to handle POST requests
def handle_post_request(headers, request):
    # Extract the Content-Length from the headers
    content_length = int([header for header in headers if "Content-Length" in header][0].split(':')[1].strip())
    # Extract the body of the request
    body = request.split('\r\n\r\n')[1][:content_length]
    # Store the dummy data
    data_store["dummy_data"] = body
    return "HTTP/1.1 200 OK\r\n\r\nData received and stored"

# Function to measure the round-trip time (RTT) of an HTTP POST request
def measure_rtt():
    start_time = time.time()  # Record the start time
    # Simulate an HTTP POST request with a delay
    time.sleep(0.1)  # Add a delay to simulate network latency
    end_time = time.time()  # Record the end time
    # Calculate the RTT
    rtt = end_time - start_time
    return rtt  # Return the RTT

# Measure RTT for 10 iterations
rtt_measurements = [measure_rtt() for _ in range(10)]
# Calculate statistical metrics
mean_rtt = statistics.mean(rtt_measurements)
median_rtt = statistics.median(rtt_measurements)
std_dev_rtt = statistics.stdev(rtt_measurements)
# Print the results
print(f"Mean RTT: {mean_rtt:.4f} seconds")
print(f"Median RTT: {median_rtt:.4f} seconds")
print(f"Standard Deviation RTT: {std_dev_rtt:.4f} seconds")

# Start the server
if __name__ == "__main__":
    start_server()
