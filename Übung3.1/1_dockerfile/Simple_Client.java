import java.io.IOException;

public class Simple_Client {
    public static void main(String[] args) throws IOException {
        
        test_get("/", 200, "Server is running");
        test_get("/status", 200, "{\"robots_active\": 5, \"current_captain\": \"Captain A\", \"controller_status\": \"Healthy\", \"dummy_data\": \"\"}");
        test_get("/captain", 200,"{\"captain\": \"Captain A\"}" );
        test_get("/health", 200, "Controller is Healthy");
        test_get("/election", 200, "New captain elected: Captain B");
        test_get("/unknown", 404, "Not Found");
        
        test_post("/", "{\"dummy_data\": \"test data\"}", 200, "Data received and stored");

    }

    private static void test_get(String path, int expStatus, String expResponse) throws IOException {
        TCP_Client client = new TCP_Client("localhost", 8080);
        HTTPResponse result = client.sendHttpRequest("GET", path, "");
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

    private static void test_post(String path, String body, int expStatus, String expResponse) throws IOException {
        TCP_Client client = new TCP_Client("localhost", 8080);
        HTTPResponse result = client.sendHttpRequest("POST", path, body);
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
