
import java.io.*;
import java.net.*;

/**
 * This code is based on the Lecture of Distributed System and Youtube Video playlist
 * https://youtube.com/playlist?list=PLoW9ZoLJX39Xcdaa4Dn5WLREHblolbji4&si=Mi1OC6Hic_-JA5AR
 */
class TCP_Client implements Runnable {

    private static final boolean DEBUG = false;
    private Socket clientSocket;

    TCP_Client(String hostIP, int hostPort) throws IOException {
        clientSocket = new Socket(hostIP, hostPort);
        if(DEBUG) System.out.println("Connected to server: " + clientSocket.getRemoteSocketAddress());
        // Handle system call to shutdown the client
        Runtime.getRuntime().addShutdownHook(new Thread(this));
    }

    public static void main(String args[]) throws Exception {
        TCP_Client client = new TCP_Client("localhost", 8080);
        while (true) {
            client.sendHttpGETRequestSystem();
        }
    }

    private String readServerResponse() throws IOException {
        BufferedReader inFromServer = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = inFromServer.readLine()) != null) {
            // add every line to the response
            response.append(line).append("\n");
        }
        String modifiedSentence = response.toString();
        if(DEBUG) System.out.println("Response from server: >\n" + modifiedSentence + "<");
        return modifiedSentence;
    }

    /**
     * Sends a HTTP GET request to the server using the system input
     * @throws IOException
     */
    private void sendHttpGETRequestSystem() throws IOException {
        BufferedReader strInput = new BufferedReader(new InputStreamReader(System.in));
        if(DEBUG) System.out.println("Write the path of the file you want to get from the server: ");
        // TODO: What is the difference between PrintWriter and DataOutputStream?
        PrintWriter outToServer = new PrintWriter(clientSocket.getOutputStream(), true);
        // DataOutputStream outToServer = new DataOutputStream(clientSocket.getOutputStream());
        String strPath = strInput.readLine();
        // Send HTTP GET request
        String httpRequest = "GET " + strPath + " HTTP/1.1\r\n" +
                "Host: localhost\r\n" +
                "Connection: close\r\n\r\n";
        outToServer.println(httpRequest);
        if(DEBUG) System.out.println("Sent to server: >\n" + httpRequest + "<");
        readServerResponse();
    }

    /**
     * Sends a HTTP GET request to the server using a given path
     * @throws IOException
     */
    public HTTPResponse sendHttpRequest(String protocol, String path, String body) throws IOException {
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

    public static HTTPResponse convertResponse(String response) throws IOException {
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
     * Splits an HTTP response into its status (headers) and body parts.
     * @param response The full HTTP response as a String.
     * @return A String array with the first element being the status
     *         (headers) and the second being the body.
     */
    public static String[] parseHttpResponse(String response) {
        // Split the response into two parts at the first blank line
        String[] parts = response.split("\n\n", 2);

        // Handle cases where body might be missing
        String status = parts[0];
        String body = parts.length > 1 ? parts[1] : "";

        return new String[] { status, body };
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

    