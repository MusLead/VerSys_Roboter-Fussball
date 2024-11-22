package clientgradle;

import org.junit.jupiter.api.*;
import java.io.*;
import java.net.*;
import static org.junit.jupiter.api.Assertions.*;

class TCP_ClientTest {

    private static final int TEST_PORT = 8081; // Test server port
    private static ServerSocket testServerSocket;
    private static Thread serverThread;

    @BeforeAll
    static void setUpServer() {
        // Start a mock server in a separate thread
        serverThread = new Thread(() -> {
            try {
                testServerSocket = new ServerSocket(TEST_PORT);
                while (true) {
                    Socket clientSocket = testServerSocket.accept();
                    BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                    PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);

                    // Read the HTTP request
                    StringBuilder request = new StringBuilder();
                    String line;
                    while ((line = in.readLine()) != null && !line.isEmpty()) {
                        request.append(line).append("\n");
                    }

                    // Create a mock HTTP response
                    String response = "HTTP/1.1 200 OK\r\n" +
                            "Content-Length: 11\r\n" +
                            "\r\n" +
                            "Hello World";

                    // Send the mock response
                    out.print(response);
                    out.flush();
                    clientSocket.close();
                }
            } catch (IOException e) {
                if (!testServerSocket.isClosed()) {
                    e.printStackTrace();
                }
            }
        });
        serverThread.start();
    }

    @AfterAll
    static void tearDownServer() throws IOException {
        if (testServerSocket != null) {
            testServerSocket.close();
        }
        if (serverThread != null) {
            serverThread.interrupt();
        }
    }

    @Test
    void testHttpRequest() throws Exception {
        // Test the HTTP request functionality of the TCP_Client
        TCP_Client client = new TCP_Client("localhost", TEST_PORT);
        HTTPResponse response = client.httpRequest("GET", "/test", "");

        // Validate the response
        assertEquals(200, response.status(), "Expected HTTP status 200");
        assertEquals("Hello World\n", response.body(), "Expected HTTP body 'Hello World'");

        client.close();
    }

    @Test
    void testServerConnectionFailure() {
        // Test client behavior when the server is unreachable
        Exception exception = assertThrows(IOException.class, () -> {
            new TCP_Client("localhost", 9999); // Non-existing server port
        });
        assertTrue(exception.getMessage().contains("Connection refused"));
    }

    @Test
    void testInvalidServerResponse() throws Exception {
        // Simulate an invalid server response
        try (ServerSocket mockServerSocket = new ServerSocket(8082)) {
            Thread mockServer = new Thread(() -> {
                try {
                    Socket clientSocket = mockServerSocket.accept();
                    while (true) {// Keep the connection open
                        // Wait for the client to send a request
                        BufferedInputStream in = new BufferedInputStream(clientSocket.getInputStream());
                        if (in.read() != -1) { 
                            // whatever the client sends, send an invalid response
                            // and close the connection
                            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
                            out.print("INVALID RESPONSE");
                            out.flush();
                            clientSocket.close();
                            break;
                        }
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
            mockServer.start();

            TCP_Client client = new TCP_Client("localhost", 8082);
            IOException exception = assertThrows(IOException.class, () -> {
                client.httpRequest("GET", "/invalid", "");
            });
            assertTrue(exception.getMessage().contains("Invalid response from server"));

            client.close();
            mockServer.join();
        }
    }
}

