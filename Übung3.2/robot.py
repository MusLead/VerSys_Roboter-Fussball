import http.client
import json
import grpc
import robot_controller_pb2
import robot_controller_pb2_grpc

# Define the host and port for the server
HOST = "localhost"
PORT = 8080

# Function to test GET requests
def test_get(path, expected_status, expected_response):
    conn = http.client.HTTPConnection(HOST, PORT)
    conn.request("GET", path)
    response = conn.getresponse()
    data = response.read().decode()
    
    print(f"GET {path}:")
    print(f"Expected Status: {expected_status}, Actual Status: {response.status}")
    print(f"Expected Response: {expected_response}, Actual Response: {data}")
    print("Pass" if response.status == expected_status and expected_response in data else "Fail")
    print("-" * 40)
    conn.close()

# Function to test POST requests
def test_post(path, payload, expected_status, expected_response):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/json", "Content-Length": str(len(payload))}
    conn.request("POST", path, payload, headers)
    response = conn.getresponse()
    data = response.read().decode()
    
    print(f"POST {path} with payload {payload}:")
    print(f"Expected Status: {expected_status}, Actual Status: {response.status}")
    print(f"Expected Response: {expected_response}, Actual Response: {data}")
    print("Pass" if response.status == expected_status and expected_response in data else "Fail")
    print("-" * 40)
    conn.close()

def register_with_controller(stub, robot_id):
    robot_info = robot_controller_pb2.RobotInfo(id=robot_id, ip="127.0.0.1")
    response = stub.RegisterRobot(robot_info)
    print(response.message)

def send_status_update(stub, robot_id, status):
    robot_status = robot_controller_pb2.RobotStatus(id=robot_id, status=status)
    response = stub.SendStatus(robot_status)
    print(response.message)

def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = robot_controller_pb2_grpc.RobotControllerStub(channel)
        register_with_controller(stub, "robot1")
        send_status_update(stub, "robot1", "Healthy")

if __name__ == "__main__":
    main()
    # Test cases
    test_get("/", 200, "Server is running")
    test_get("/status", 200, json.dumps({"robots_active": 5, "current_captain": "Captain A", "controller_status": "Healthy", "dummy_data": ""}))
    test_get("/captain", 200, json.dumps({"captain": "Captain A"}))
    test_get("/health", 200, "Controller is Healthy")
    test_get("/election", 200, "New captain elected: Captain B")
    test_get("/unknown", 404, "Not Found")

    # Test POST request with dummy data
    test_post("/", json.dumps({"dummy_data": "test data"}), 200, "Data received and stored")

