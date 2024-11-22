package clientgradle;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * A simple HTTP client that sends GET and POST requests to a server and prints the results.
 * This client tests the server's response status and body content.
 */
public class Simple_Client {
    protected static String host = "localhost";
    private static final int PORT = 8080;

    /**
     * Sends a GET request to the server with the given path, and prints the results.
     * @param path the path of the GET request
     * @param expStatus the expected status code of the server response
     * @param expResponse the expected response body of the server
     * @throws IOException
     */
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

    /**
     * Sends a POST request to the server with the given path and body, and prints the results.
     * @param path the path of the POST request
     * @param body the body of the POST request
     * @param expStatus the expected status code of the server response
     * @param expResponse the expected response body of the server
     * @throws IOException
     */
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

    /**
     * Sends a POST request to the server with the given path and body, and measures the Round-Trip Time (RTT) of the request.
     * @param path the path of the POST request
     * @param body the body of the POST request
     * @param expStatus the expected status code of the server response
     * @param expResponse the expected response body of the server
     * @throws IOException
     */
    public static void test_post_with_rtt(String path, String body, int expStatus, String expResponse) throws IOException {
        List<Long> rtts = new ArrayList<>();
        int iterations = 10; // Anzahl der Wiederholungen
        for (int i = 0; i < iterations; i++) {
            long startTime = System.nanoTime();
            TCP_Client client = new TCP_Client(host, PORT);
            HTTPResponse result = client.httpRequest("POST", path, body);
            long endTime = System.nanoTime();

            int status = result.status();
            String response = result.body();
            long rtt = (endTime - startTime) / 1_000_000; // Zeit in Millisekunden
            rtts.add(rtt);

            String resultStatus = (status == expStatus && response.contains(expResponse)) ? "Pass" : "FAIL!!!!!!";
            System.out.println("POST " + path + " (Run " + (i + 1) + "):");
            System.out.println("RTT: " + rtt + " ms");
            System.out.println("Expected Status: " + expStatus + ", Actual Status: " + status);
            System.out.println("Expected Response: " + expResponse + ", Actual Response: " + response);
            System.out.println(resultStatus);
            System.out.println("----------------------------------------");

            client.close();
        }
        evaluateStatistics(rtts);
    }


    /**
     * Evaluates and prints the statistics of Round-Trip Times (RTTs) from a list of RTT values.
     *
     * The method calculates and prints the following statistics:
     * - Total number of RTT values
     * - Mean RTT
     * - The longest and shortest RTT values
     * - The list of RTT values
     *
     * @param rtts a list of RTT values in milliseconds
     * 
     */
    private static void evaluateStatistics(List<Long> rtts) {
        double mean = rtts.stream().mapToLong(Long::longValue).average().orElse(0.0);
        double longest = rtts.stream().mapToLong(Long::longValue).max().orElse(0);
        double shortest = rtts.stream().mapToLong(Long::longValue).min().orElse(0);

        System.out.println("\n--- RTT Statistics ---");
        System.out.println("Total Runs: " + rtts.size());
        System.out.println("Mean RTT: " + mean + " ms");
        System.out.println("Longest RTT: " + longest + " ms");
        System.out.println("Shortest RTT: " + shortest + " ms");
        System.out.println("RTTs: " + rtts);
        System.out.println("-----------------------");
    }

}
