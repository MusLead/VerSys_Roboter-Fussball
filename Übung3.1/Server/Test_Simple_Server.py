import time
from Simple_Server import test_start_server
import unittest
import socket
import threading

shutdown_event = threading.Event()  # Shared shutdown event for the server thread

# Start the server in a separate thread
def start_server_thread():
    """
    Start the server in a separate thread and use a shutdown event for termination.
    """
    thread = threading.Thread(target=test_start_server, daemon=True)
    thread.start()
    return thread

class TestHTTPServer(unittest.TestCase):
    # server_thread = None  # Class-level variable for the server thread
    shutdown_event = threading.Event()
    port = 8080  # Default port

    @classmethod
    def setUpClass(cls):
        """
        Start the server before running tests.
        """
        cls.shutdown_event.clear()
        cls.server_thread = threading.Thread(
            target=start_server, args=(cls.shutdown_event,), daemon=True
        )
        cls.server_thread.start()
        time.sleep(1)  # Give the server time to start
        print("Server thread started.")

    @classmethod
    def tearDownClass(cls):
        """
        Stop the server after all tests are completed.
        """
        cls.shutdown_event.set()  # Signal the server to stop
        cls.server_thread.join()  # Wait for the server thread to finish
        print("Server has been shut down.")

    def send_request(self, request):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(('127.0.0.1', 8080))
            client_socket.sendall(request.encode('utf-8'))
            response = client_socket.recv(4096).decode('utf-8')
        return response

    def test_get_status(self):
        request = "GET /status HTTP/1.1\r\nHost: localhost\r\n\r\n"
        response = self.send_request(request)
        self.assertIn("200 OK", response)
        self.assertIn('"robots_active": 5', response)

    def test_get_captain(self):
        request = "GET /captain HTTP/1.1\r\nHost: localhost\r\n\r\n"
        response = self.send_request(request)
        self.assertIn("200 OK", response)
        self.assertIn('"captain": "Captain B"', response)

    def test_get_health(self):
        request = "GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n"
        response = self.send_request(request)
        self.assertIn("200 OK", response)
        self.assertIn("Controller is Healthy", response)

    def test_election(self):
        request = "GET /election HTTP/1.1\r\nHost: localhost\r\n\r\n"
        response = self.send_request(request)
        self.assertIn("200 OK", response)
        self.assertIn("New captain elected: Captain B", response)

    def test_reset(self):
        request = "GET /reset HTTP/1.1\r\nHost: localhost\r\n\r\n"
        response = self.send_request(request)
        self.assertIn("205 Reset Content", response)

    def test_post_dummy_data(self):
        body = '{"key": "value"}'
        request = (
            f"POST / HTTP/1.1\r\n"
            f"Host: localhost\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body)}\r\n\r\n"
            f"{body}"
        )
        response = self.send_request(request)
        self.assertIn("200 OK", response)
        self.assertIn("Data received and stored", response)

    def test_not_found(self):
        request = "GET /unknown HTTP/1.1\r\nHost: localhost\r\n\r\n"
        response = self.send_request(request)
        self.assertIn("404 Bad Request", response)

if __name__ == "__main__":
    unittest.main()
