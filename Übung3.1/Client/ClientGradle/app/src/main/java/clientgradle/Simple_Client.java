package clientgradle;

import java.io.IOException;

public class Simple_Client {
    protected static String host = "localhost";
    private static final int PORT = 8080;

    public static void test_get(String path, int expStatus, String expResponse) throws IOException {
        System.out.println("Starting Host: " + host);
        TCP_Client client = new TCP_Client(host, PORT);
        HTTPResponse result = client.httpRequest("GET", path, "");
        int status = result.status();
        String response = result.body();

        String resultStatus = status == expStatus && response.contains(expResponse) ? "Pass" : "FAIL!!!!!!";
        System.out.println("POST " + path + ":");
        System.out.println("Expected Status: " + expStatus + ", Actual Status: " + status);
        System.out.println("Expected Response: " + expResponse + ", Actual Response: " + response);
        System.out.println(resultStatus);
        System.out.println("----------------------------------------");

        client.close();
    }

    public static void test_post(String path, String body, int expStatus, String expResponse) throws IOException {
        TCP_Client client = new TCP_Client(host, PORT);
        HTTPResponse result = client.httpRequest("POST", path, body);
        int status = result.status();
        String response = result.body();

        String resultStatus = status == expStatus && response.contains(expResponse) ? "Pass" : "FAIL!!!!!!";
        System.out.println("POST " + path + ":");
        System.out.println("Expected Status: " + expStatus + ", Actual Status: " + status);
        System.out.println("Expected Response: " + expResponse + ", Actual Response: " + response);
        System.out.println(resultStatus);
        System.out.println("----------------------------------------");

        client.close();
    }
}
