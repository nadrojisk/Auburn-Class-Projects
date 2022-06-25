import java.io.File;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.Scanner;

/**
 * UDPServer Class
 * Runs on Server machine to send HTML files to Client
 * Compile using java UDPServer
 * Use tux050 - tux065 when running
 *
 * @author Stephanie Parrish, Jordan Sosnowski, Marcus Woodard
 * @version 7.15.18
 */
public class SR_UDPServer {

    private static final double ALPHA = .125;
    private static final double BETA = .25;

    public static void main(String args[]) throws Exception {

        int[] ports = {10028, 10029, 10030, 10031}; //list of port numbers assigned to our group to use
        int port = ports[0];
        System.out.print("Getting IP Address..."); //remove later
        String localhost = InetAddress.getLocalHost().getHostAddress().trim();  //grabs IP to use for Client
        System.out.println("\nConnected to: " + localhost); //prints out the Server IP

        DatagramSocket serverSocket = new DatagramSocket(port);


        byte[] receiveData = new byte[512]; //create bytes for sending/receiving data

        Scanner readFileIn;  //Create an instance of the Scanner class so files can be read in

        while (true) {
            System.out.println("Ready to Receive Transmission...");
            StringBuilder fileDataContents = new StringBuilder();   //variable for the file data contents
            DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length); //Creates a new datagram
            serverSocket.receive(receivePacket);
            System.out.println("Receiving the request packet.");

            //Gets the IPAddress and Port number of Host
            InetAddress IPAddress = receivePacket.getAddress();
            int portReceive = receivePacket.getPort();


            String dataFromClient = new String(receivePacket.getData()); //Gets the data for the packet from host

            ///File Data read in/////////
            //gets the data that needs to be read which is the packet data from above
            //The next few lines will check the filename for white space make sure file name is correct
            readFileIn = new Scanner(dataFromClient);

            readFileIn.next(); //skips the GET command of the HTTP request message to just read in the TestFile
            String fileName = readFileIn.next(); //grabs file name
            readFileIn.close(); //closes the file

            try {
                readFileIn = new Scanner(new File(fileName));  //File requested by host
            } catch (Exception e) {   //if file not found, crashes gracefully
                System.out.println(e.getClass());
                serverSocket.send(setNullPacket(IPAddress, portReceive));
                continue;
            }
            while (readFileIn.hasNext()) {  //get the contents of the file line by line
                fileDataContents.append(readFileIn.nextLine());
            }
            System.out.println("File: " + fileDataContents); //print the file contents received
            readFileIn.close(); //close the file


            //Header Form given by Lab document
            String HTTP_HeaderForm = "HTTP/1.0 200 Document Follows\r\n"
                    + "Content-Type: text/plain\r\n"
                    + "Content-Length: " + fileDataContents.length() + "\r\n"
                    + "\r\n" + fileDataContents;


            //////////////////////////////////////////////////////////////////////////////////////
            ArrayList<SR_Packet> PacketList = SR_Packet.Segmentation(HTTP_HeaderForm.getBytes()); //segments file into packets
            ArrayList<SR_Packet> windowList = new ArrayList<>();


            ArrayList<Double> sendTimes = new ArrayList<>();
            ArrayList<Double> ackReceiveTime = new ArrayList<>();
            ArrayList<Double> estRTT = new ArrayList<>();
            estRTT.add(40.0);
            ArrayList<Double> devRTT = new ArrayList<>();
            devRTT.add(0.0);
            ArrayList<Double> timeoutRTT = new ArrayList<>();
            timeoutRTT.add(calculateTimeoutRtt(0, estRTT.get(0), devRTT.get(0)));

            int packetNumber = 0;

            while (packetNumber < PacketList.size()) {
                while (windowList.size() < 8 && packetNumber < PacketList.size()) { //once size hit...waits for ACKs{
                    DatagramPacket sendPacket = PacketList.get(packetNumber).getDatagramPacket(IPAddress, portReceive);
                    serverSocket.send(sendPacket);
                    windowList.add(PacketList.get(packetNumber)); //adds packet to window
                    System.out.println("Sending Packet " + (packetNumber % 24) + " of 23");
                    sendTimes.add(getTimeInDouble());
                    packetNumber = (packetNumber + 1);
                }
                { //if window if filled loop until window empty
                    while (windowList.size() > 0) {
                        receiveData = new byte[512]; //create bytes for sending/receiving data
                        DatagramPacket clientResponse = new DatagramPacket(receiveData, receiveData.length); //Creates a new datagram
                        serverSocket.setSoTimeout(40); //TODO Marcus
                        try {
                            serverSocket.receive(clientResponse);
                        } catch (SocketTimeoutException e) {
                            DatagramPacket sendPacket = windowList.get(0).getDatagramPacket(IPAddress, portReceive);
                            serverSocket.send(sendPacket);
                            System.out.println("Re-Sending Lost Packet " + (windowList.get(0).getHeaderValue(SR_Packet.HEADER_ELEMENTS.SEGMENT_NUMBER)) + " of 23");
                            sendTimes.add(getTimeInDouble());
                            continue;
                        }
                        String responseFromClient = new String(clientResponse.getData()).trim();
                        if (responseFromClient.contains("ACK")) { //receiving ACK
                            String[] ackSplit = responseFromClient.split(":");
                            String ackNum = ackSplit[1];
                            System.out.println("Receiving ACK: " + ackNum);
                            for (SR_Packet packet : windowList) {
                                if (packet.getHeaderValue(SR_Packet.HEADER_ELEMENTS.SEGMENT_NUMBER).trim().equals(ackNum)) {
                                    packet.acked();
                                    break;
                                }
                            }
                            while (windowList.size() > 0 && windowList.get(0).isAcked()) {
                                windowList.remove(0);
                            }
                        } else if (responseFromClient.contains("NAK")) { //receiving NAK //TODO this is where the error is
                            String[] nakSplit = responseFromClient.split(":");
                            String nakNum = nakSplit[1];
                            System.out.println("Receiving NAK: " + nakNum);
                            if (windowList.size() <= 8) {
                                DatagramPacket resendPacket = PacketList.get(Integer.parseInt(nakNum)).getDatagramPacket(IPAddress, portReceive);
                                serverSocket.send(resendPacket);
                                System.out.println("Re-Sending Packet " + nakNum + " of 23");
                            }
                        }
                    }
                }
            }

            //Sends Null Packet to let host know transfer is over
            serverSocket.send(setNullPacket(IPAddress, portReceive));
            return;
        }
    }

    /**
     * setNullPacket
     * Creates null packet to send to client to signify end of transmission
     *
     * @param IPAddress:   IP Address of Client
     * @param portReceive: Port of Client
     * @return returns Null Datagram Packet to send to Client
     */
    private static DatagramPacket setNullPacket(InetAddress IPAddress, int portReceive) {
        String nullByte = "\0";
        ArrayList<SR_Packet> nullPacket = SR_Packet.Segmentation(nullByte.getBytes());    //null packet changed to full 256 bit size, but only contains 1 bit of info
        DatagramPacket nullDatagram = nullPacket.get(0).getDatagramPacket(IPAddress, portReceive);
        System.out.println("Sending Null Packet");
        return nullDatagram;
    }

    private static double calculateEstRtt(double sampRttIn, double estRttIn) {
        return (1 - ALPHA) * estRttIn + ALPHA * sampRttIn;
    }

    private static double calculateDevRtt(double sampRttIn, double devRttIn) {
        return (1 - BETA) * devRttIn + BETA * Math.abs(sampRttIn + devRttIn);
    }

    private static double calculateTimeoutRtt(double sampRttIn, double estRttIn, double devRttIn) {
        return calculateEstRtt(sampRttIn, estRttIn) + 4 * calculateDevRtt(sampRttIn, devRttIn);
    }

    private static double getTimeInDouble() {
        return Double.parseDouble(Long.toString(System.currentTimeMillis()));
    }
}
