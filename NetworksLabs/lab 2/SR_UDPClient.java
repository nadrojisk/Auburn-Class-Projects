import java.awt.*;
import java.io.File;
import java.io.FileWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.ArrayList;
import java.util.Random;

/**
 * UDPClient Class.
 * Runs on Client machine to request HTML files from Server
 * Compile using java UDPClient <chanceOfCorruption>
 * <p>
 * Use tux050 - tux065 when running on tux,
 * Make sure to change IPADDRESSOFSERVER to the correct IP
 *
 * @author Stephanie Parrish, Jordan Sosnowski, Marcus Woodard
 * @version 7.15.18
 */
public class SR_UDPClient {

    private static final String IPADDRESSOFSERVER = "131.204.14.51";

    public static void main(String args[]) throws Exception {

        int[] ports = {10028, 10029, 10030, 10031}; //Group Assigned Port Numbers
        int port = ports[0];

        DatagramSocket clientSocket = new DatagramSocket();                  //creates socket for user
        InetAddress IPAddress = InetAddress.getByName(IPADDRESSOFSERVER);    //gets IP address of Server

        byte[] sendData;    //creates packet to be sent
        byte[] receiveData = new byte[512]; //creates packet to be received
        String[] GremlinProbability = new String[]{"0.0", "0.0"};
        boolean DataDoneSending = false;
        int packetNumber = 0;

        // ********** SETUP GREMLIN **********
        //use command line arguments to detect Gremlin probability
        //checks for no arguments and if there are none then notify user and
        if (args.length != 2) {
            System.out.println("There are no arguments detected for Gremlin Probability");
        } else {
            //if there is arguments then set the Gremlin Probability to these
            GremlinProbability[0] = args[0];
            GremlinProbability[1] = args[1];
        }

        // ********** SENDING DATA **********
        String TestFile = "GET TestFile.html HTTP/1.0"; //request to be sent to Server
        sendData = TestFile.getBytes(); //gets request in byte form

        //sends request to server
        DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, IPAddress, port);
        clientSocket.send(sendPacket);

        System.out.println("Sending request packet...."); //notify user of sending

        // ********** RECEIVING PACKETS **********
        System.out.println("Receiving packets...");

        DatagramPacket receivePacket; //Declares the Datagram packet for receive packet
        ArrayList<SR_Packet> receivedPackets = new ArrayList<>(); //create a new array of packets received
        while (!DataDoneSending) { //check to see if the data is done sending to host

            receivePacket = new DatagramPacket(receiveData, receiveData.length); //creates a null datagram packet
            clientSocket.receive(receivePacket); //receives the actual packet from the server
            //create a packet from the data received
            if(packetNumber == 30){
                System.out.println("HI");
            }
            SR_Packet createReceivedPacket = SR_Packet.CreatePacket(receivePacket);

            System.out.println("Receiving Packet: " + createReceivedPacket.getHeaderValue(SR_Packet.HEADER_ELEMENTS.SEGMENT_NUMBER));
            //checks to see if the packet data is null
            //if it is then that means the data is done sending and it will break out of the loop
            if (createReceivedPacket.GETPacketData()[0] == '\0') {
                DataDoneSending = true;
                if (receivedPackets.size() == 0) {
                    System.out.println("Error File Not Found");
                    return;
                }
            } else {
                //send each of the packets with arguments through the Gremlin function to
                //determine whether to change some of the packet bit or pass the packet as it is to the receiving function

                if (!Gremlin(GremlinProbability, createReceivedPacket)) { //if false packet lost -> do not run error detection
                    //Check for error detection in the received packets
                    if (ErrorDetection(createReceivedPacket)) { //if error detected send NAK
                        //gets the segment number of unacknowledged packet
                        String NAK = "Sending NAK:" + createReceivedPacket.getHeaderValue(SR_Packet.HEADER_ELEMENTS.SEGMENT_NUMBER); //NAK sent back to the server
                        System.out.println(NAK);
                        byte[] nakData = NAK.getBytes(); //gets request in byte form

                        //sends NAK to the serverSocket
                        DatagramPacket sendNAK = new DatagramPacket(nakData, nakData.length, IPAddress, port);
                        clientSocket.send(sendNAK);
                    } else{//if error not detected send ACK
                        receivedPackets.add(createReceivedPacket); //received packets are added to the packet array
                        String ACK = "Sending ACK:" + createReceivedPacket.getHeaderValue(SR_Packet.HEADER_ELEMENTS.SEGMENT_NUMBER); //request to be sent to Server
                        System.out.println(ACK);
                        packetNumber++;
                        byte[] ackData = ACK.getBytes(); //gets request in byte form

                        //sends ACK to server
                        DatagramPacket sendACK = new DatagramPacket(ackData, ackData.length, IPAddress, port);
                        clientSocket.send(sendACK);
                    }
                }
                else{
                    System.out.println("Packet Lost: " + createReceivedPacket.getHeaderValue(SR_Packet.HEADER_ELEMENTS.SEGMENT_NUMBER));
                }
            }
        }

        //Reassembles Packets that were received
        ArrayList<SR_Packet> arrangedPackets = new ArrayList<>();
        byte[] ReassemblePacketFile = SR_Packet.ReassemblePacket(receivedPackets);
        String modifiedPacketData = new String(ReassemblePacketFile);
        System.out.println("Packet Data Received from UDPServer:\n" + modifiedPacketData);
        clientSocket.close();

        //Display packets using a Web browser
        int index = modifiedPacketData.lastIndexOf("\r\n", 100);
        modifiedPacketData = modifiedPacketData.substring(index);

        //if running on Tux don't display HTML on browser since it will crash
        if (!System.getProperty("os.name").equals("Linux")) {
            //creates a temporary TestFile
            File TestFileTemp = File.createTempFile("TestFile", ".html");
            FileWriter writer = new FileWriter(TestFileTemp);
            writer.write(modifiedPacketData);
            writer.close();
            //opens the test file on the desktop
            Desktop desk = Desktop.getDesktop();
            desk.open(TestFileTemp);
        }

    }

    /**
     * Gremlin function
     * Gremlin will damage bits depending on runtime user argument, number of bits also depends on probability
     * P(1 byte damaged) = 50%
     * P(2 bytes damaged) = 30%
     * P(3 bytes damaged) = 20%
     *
     * @param gremlin_args:   probability that a bit will be damaged or lost
     * @param receivedPacket: packet to be damaged by gremlin
     * @return True:  Packet lost
     **/
    private static boolean Gremlin(String[] gremlin_args, SR_Packet receivedPacket) {
        Random random = new Random();

        int dmgRand = random.nextInt(100) + 1; //pick a random number between 1 - 100
        int howManyRand = random.nextInt(100) + 1; //pick a random number between 1 - 100
        int bytesToChange;
        String lostPackets = gremlin_args[0];
        String damagedPackets = gremlin_args[1];

        double lostProbability = Double.parseDouble(lostPackets) * 100;
        double damagedProbability = Double.parseDouble(damagedPackets) * 100;
        //if the packet is lost then it returns true
        if (dmgRand <= lostProbability) {
            return true;
        }
        if (dmgRand <= damagedProbability) {
            if (howManyRand <= 50) {    //Change only 1 Byte
                bytesToChange = 1;
            } else if (howManyRand <= 80) { //Change 2 Bytes
                bytesToChange = 2;
            } else bytesToChange = 3; //Change 3 Bytes
            if (dmgRand <= damagedProbability) { //if probability to change bytes is hit
                for (int i = 0; i <= bytesToChange; i++) {
                    byte[] data = receivedPacket.GETPacketData();
                    int byteToCorrupt = random.nextInt(receivedPacket.getPacketDataSize()); // pick a random byte
                    data[byteToCorrupt] = (byte) ~data[byteToCorrupt]; // flip the bits in that byte
                }
            }
        }
        return false;
    }

    /**
     * ErrorDetection function
     * Detects if packet was damaged by Gremlin function, prints packet number of corrupted packet
     *
     * @param aPacketList: list of packets received by Client
     * @return True if error detected, false if error not detected
     */
    private static boolean ErrorDetection(SR_Packet aPacketList) {
        String strReceivedCheckSum = aPacketList.getHeaderValue(SR_Packet.HEADER_ELEMENTS.CHECKSUM);
        Short receivedCheckSum = Short.parseShort(strReceivedCheckSum);

        byte[] data = aPacketList.GETPacketData();
        short calcCheckSum = SR_Packet.CheckSum(data);
        if (!receivedCheckSum.equals(calcCheckSum)) { //Checks to see if packets prior checksum is equal to current checksum
            System.out.println("Error detected in Packet Number: " + aPacketList.getHeaderValue(SR_Packet.HEADER_ELEMENTS.SEGMENT_NUMBER));
            return true;
        } else
            return false;

    }

}
