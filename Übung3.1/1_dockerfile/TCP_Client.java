
import java.io.*;
import java.net.*;

class TCP_Client implements Runnable {
    private Socket clientSocket;

    public static void main(String args[]) throws Exception {
        // Handle system call to shutdown the client
        Runtime.getRuntime().addShutdownHook(new Thread(this));
        
        String serverIP = "localhost";
        int serverPort = 8080;
        start_client(serverIP, serverPort, clientSocket);
    }

    private static void start_client(String hostIP, int hostPort, Socket clientSocket) throws IOException {
        while (true) {
            clientSocket = new Socket(hostIP, hostPort);
            sendHttpGetRequest(clientSocket);
            readServerResponse(clientSocket);
        }
    }

    private static void readServerResponse(Socket clientSocket) throws IOException {
        BufferedReader inFromServer = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = inFromServer.readLine()) != null) {
            response.append(line).append("\n");
        }
        String modifiedSentence = response.toString();
        System.out.println("Response from server: >\n" + modifiedSentence + "<");
        clientSocket.close();
    }

    private static void sendHttpGetRequest(Socket clientSocket) throws IOException {
        BufferedReader strInput = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("Write the path of the file you want to get from the server: ");
        // TODO: What is the difference between PrintWriter and DataOutputStream?
        PrintWriter outToServer = new PrintWriter(clientSocket.getOutputStream(), true);
        // DataOutputStream outToServer = new
        // DataOutputStream(clientSocket.getOutputStream());
        String strPath = strInput.readLine();
        // Send HTTP GET request
        String httpRequest = "GET " + strPath + " HTTP/1.1\r\n" +
                "Host: localhost\r\n" +
                "Connection: close\r\n\r\n";
        outToServer.println(httpRequest);
        System.out.println("Sent to server: >\n" + httpRequest + "<");
    }

    @Override
    public void run() {
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

    