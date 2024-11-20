
import java.io.*;
import java.net.*;

/**
 * This code is based on the Lecture of Distributed System and Youtube Video playlist
 * https://youtube.com/playlist?list=PLoW9ZoLJX39Xcdaa4Dn5WLREHblolbji4&si=Mi1OC6Hic_-JA5AR
 * 
 * This implementation is based on HTTP-Server with only 2 Protocols (GET and POST)
 */
class TCP_Client implements Runnable {

    private static final boolean DEBUG = true;
    private Socket clientSocket;

    TCP_Client(String hostIP, int hostPort) throws IOException {
        try {
            clientSocket = new Socket(hostIP, hostPort);
        } catch (IOException e) {
            System.err.println("Could not connect to server, make sure the server is online and reachable!\n\n");
            throw e;
        }
        if(DEBUG) System.out.println("Connected to server: " + clientSocket.getRemoteSocketAddress());
        // Handle system call to shutdown the client
        Runtime.getRuntime().addShutdownHook(new Thread(this));
    }

    public static void main(String args[]) throws Exception {
        // For testing purposes
        while (true) {
            TCP_Client client = new TCP_Client("localhost", 8080);
            System.out.println("Write the path of the file you want to get from the server: ");
            BufferedReader strInput = new BufferedReader(new InputStreamReader(System.in));
            String strPath = strInput.readLine();
            HTTPResponse httpResponse = client.httpRequest("GET",strPath,"");
            System.out.println("Status: " + httpResponse.status() + "\nBody: " + httpResponse.body());
            client.close();
        }
    }

    /**
     * Reads the server response and returns it as a String.
     * @return The server response as a String.
     * @throws IOException
     */
    private String readServerResponse() throws IOException {
        BufferedReader inFromServer = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = inFromServer.readLine()) != null) {
            // Add every line of Server-responses to the response
            response.append(line).append("\n");
        }
        String modifiedSentence = response.toString();
        if(DEBUG) System.out.println("Response from server: >\n" + modifiedSentence + "<");
        return modifiedSentence;
    }

    /**
     * Sends a HTTP GET request to the server using a given path
     * This Method also wait for the answer from the Server. 
     * @param protocol either GET or POST will be sent to the Server
     * @param path of the HTTP
     * @param body of the request, if the request is POST
     * @return The Response from the server
     * @throws IOException
     */
    public HTTPResponse httpRequest(String protocol, String path, String body) throws IOException {
        PrintWriter outToServer = new PrintWriter(clientSocket.getOutputStream(), true);
        // Send HTTP GET request
        String httpRequest = protocol + " " + path + " HTTP/1.1\r\n" +
                "Host: localhost\r\n" +
                "Connection: close\r\n" +
                "Content-Length: " + body.length() + "\r\n\r\n"
                + body;
        outToServer.println(httpRequest);
        if(DEBUG) System.out.println("Sent to server: >\n" + httpRequest + "<");
        return convertResponse(readServerResponse());
    }

    /**
     * Converts a response from the server into an HTTPResponse object.
     * @param response The full HTTP response as a String.
     * @return An HTTPResponse object with the status and body.
     * @throws IOException
     */
    public static HTTPResponse convertResponse(String response) throws IOException {
        if (response == null || response.isBlank()) {
            throw new IOException("Empty or invalid response from server. Check again if the previous socket has been closed.");
        }
        String[] responseParts = response.split("\n\n", 2);
        if (responseParts.length < 2) 
            throw new IOException("Invalid response from server: \n" + response);
        
        String[] statusLine = responseParts[0].split("\r\n");
        if (statusLine.length < 1) 
            throw new IOException("Invalid status line in response");
        
        String[] statusLineParts = statusLine[0].split(" ");
        if (statusLineParts.length < 2) 
            throw new IOException("Invalid status line parts in response");
        
        int status = Integer.parseInt(statusLineParts[1]);
        String body = responseParts[1];
        return new HTTPResponse(status, body);
    }

    /**
     * Closes the client socket, so that 
     * the the socket is not left open.
     * @throws IOException
     */
    public void close() throws IOException {
        clientSocket.close();
    }

    @Override
    public void run() {
        // This will be executed for Test-Purposes
        // Handle system call to shutdown the client (this is being implemented in the constructor)
        // https://stackoverflow.com/questions/2541475/capture-sigint-in-java
        try {
            if(!clientSocket.isClosed()){
                clientSocket.close();
                System.out.println("\nShutdown gracefully");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}

record HTTPResponse(int status, String body) {}

    