import java.net.*;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * This class contains the methods used for packets including creating a packet, getting packet data,
 * getting/setting the packet header, getting/setting the packet segment number, segmentation, re-assembly,
 * and the check sum function
 *
 * @author StephanieParrish, Jordan Sosnowski, and Marcus Woodard
 * @version 7/15/2018
 */

class SR_Packet {

    ///////Package Header///////
    //Constant Variables
    //Private constant to map segment number and checksum
    private static final String HEADER_SEGMENT_NUMBER = "SegmentNumber";
    private static final String HEADER_CHECKSUM = "CheckSum";
    private static final String HEADER_MODULO_NUMBER = "ModNum";
    private static final int HEADER_LINES = 6;  //Number of header lines that go before the objects to be sent given in the lab assignment
    //package data
    private static int PACKET_SIZE = 512;  //Size of the packets to be sent
    private static final int PACKET_DATA_SIZE = PACKET_SIZE - HEADER_LINES; //Size of the data that is transmitted in the packet
    private byte[] PackageData;
    //Map data dictionary that maps the header string to strings
    private Map<String, String> PacketHeader;
    private boolean isAcked = false;

    //Constructor
    private SR_Packet() {
        //Initialize data array
        PackageData = new byte[PACKET_SIZE];

        //Initialize Map using HashMap
        PacketHeader = new HashMap<>();
    }

    //Reassemble Packet function called by the UDPClient. Takes in the list of segmented packets and re-assembles them.
    static byte[] ReassemblePacket(ArrayList<SR_Packet> PacketList) {
        ArrayList<SR_Packet> arrangePackets = new ArrayList<>();
        int totalSize = 0;
        //gets packet data size for each of the segmented packets
        for (SR_Packet aPacketList : PacketList) totalSize += aPacketList.getPacketDataSize();
        //creates a byte that will contain the total size for the final returned packet
        byte[] returnPacket = new byte[totalSize];
        int returnCounter = 0;
        for (int i = 0; i < PacketList.size(); i++) {
            //Search the packetList for each packet
            for (SR_Packet FindPacket : PacketList) {
                //gets packet by segment number
                String segmentNumber = FindPacket.getHeaderValue(HEADER_ELEMENTS.SEGMENT_NUMBER);
                String moduloNumber = FindPacket.getHeaderValue(HEADER_ELEMENTS.MODULO_NUMBER);
                int finalNumber = Integer.parseInt(segmentNumber) + (24 * Integer.parseInt(moduloNumber));
                //gets the packet data size and data that match the segment number found
                if (finalNumber == i) {
                    for (int k = 0; k < FindPacket.getPacketDataSize(); k++)
                        returnPacket[returnCounter + k] = FindPacket.GETPacketData(k);
                    returnCounter += FindPacket.getPacketDataSize();
                    arrangePackets.add(FindPacket);
                    break;
                }
            }
        }
        //returns the packet that has been re-assembled
        return returnPacket;
    }

    //Segmentation is called by the UDPServer to break the packets into segments
    static ArrayList<SR_Packet> Segmentation(byte[] fileBytes) {
        //creates an empty array list for the newly segmented packets
        ArrayList<SR_Packet> returnPacket = new ArrayList<>();
        //gets the fileBytes length
        int fileLength = fileBytes.length;
        //if the file has a length zero then throws an error saying the file is empty
        if (fileLength == 0) {
            throw new IllegalArgumentException("File Empty");
        }
        int byteCounter = 0;
        int segmentNumber = 0;
        int modCounter = 0;
        int index = 0;
        //checks the fileLength against the byte counter.
        //As long as the byteCounter is less than the file length a new SR_Packet will be created of size 252
        while (byteCounter < fileLength) {
            SR_Packet nextPacket = new SR_Packet();
            byte[] nextPacketData = new byte[PACKET_DATA_SIZE];
            //read in amount of data size 512 (total) - 6 (header) = 506 (data)
            int readInDataSize = PACKET_DATA_SIZE; //only allows 506 bytes since the other 4 are for the header
            //as long as the file length - the number of bytes counted is less than 252
            //then more data is added to the packet segment
            if (fileLength - byteCounter < PACKET_DATA_SIZE) {
                readInDataSize = fileLength - byteCounter;
            }
            //copy the file data
            int j = byteCounter;
            for (int i = 0; i < readInDataSize; i++) {
                nextPacketData[i] = fileBytes[j];
                j++;
            }

            //set the packet data for the next packet
            nextPacket.setPacketData(nextPacketData);

            //set the header for the next packet
            nextPacket.setHeaderValue(HEADER_ELEMENTS.SEGMENT_NUMBER, segmentNumber + "");
            nextPacket.setHeaderValue(HEADER_ELEMENTS.MODULO_NUMBER, modCounter + "");
            //CheckSum (errors)
            String CheckSumPacket = String.valueOf(SR_Packet.CheckSum(nextPacketData));
            nextPacket.setHeaderValue(HEADER_ELEMENTS.CHECKSUM, CheckSumPacket);
            returnPacket.add(nextPacket);

            //increase the segment number
            index++;
            modCounter = (index) / 24;
            segmentNumber = (segmentNumber + 1) % 24;

            //increase the counter by the amount read in
            byteCounter = byteCounter + readInDataSize;
        }

        return returnPacket;
    }

    //Creates a new packet
    static SR_Packet CreatePacket(DatagramPacket packet) {
        SR_Packet newPacket = new SR_Packet();
        ByteBuffer bytebuffer = ByteBuffer.wrap(packet.getData()); //wraps the byte array into the buffer
        newPacket.setHeaderValue(HEADER_ELEMENTS.SEGMENT_NUMBER, bytebuffer.getShort() + ""); //sets header segment number
        newPacket.setHeaderValue(HEADER_ELEMENTS.CHECKSUM, bytebuffer.getShort() + ""); //sets header checksum
        newPacket.setHeaderValue(HEADER_ELEMENTS.MODULO_NUMBER, bytebuffer.getShort() + "");
        byte[] PacketData = packet.getData(); //gets the packet data
        byte[] remaining = new byte[PacketData.length - bytebuffer.position()]; //subtracts the package data length from the byte buffer position
        //copies  an array from the specified source array, beginning at the specified position, to the specified position of the destination array
        System.arraycopy(PacketData, bytebuffer.position(), remaining, 0, remaining.length);
        newPacket.setPacketData(remaining); //sets the packet data
        return newPacket; //returns the newly created packet
    }

    //Check sum function that return the 16 bit checkSum value for a packet
    static short CheckSum(byte[] packetBytes) {
        long sum = 0;
        //gets length of the packetBytes Array
        int packetByteLength = packetBytes.length;
        int count = 0;
        while (packetByteLength > 1) { //while the length is greater than 1 then the bits will be shifted left
            //get the packetByte in the array of the count shift it left 8 bits
            sum += ((packetBytes[count]) << 8 & 0xFF00) | ((packetBytes[count + 1]) & 0x00FF);
            //if a carry occurred then it is wrapped around
            if ((sum & 0xFFFF0000) > 0) {
                sum = ((sum & 0xFFFF) + 1);
            }
            //increase count by 2
            //decrease packet byte length by 2
            count += 2;
            packetByteLength -= 2;
        }

        if (packetByteLength > 0) {
            sum += (packetBytes[count] << 8 & 0xFF00);
            if ((sum & 0xFFFF0000) > 0) {
                sum = ((sum & 0xFFFF) + 1);
            }
        }
        //inverts the sum by getting the unary bitwise complement
        return (short) (~sum & 0xFFFF);
    }

    void acked() {
        isAcked = true;
    }

    /////////////////////////PACKAGE HEADER METHODS//////////////////////////////////

    boolean isAcked() {
        return isAcked;
    }

    //Get Header Element Values
    String getHeaderValue(HEADER_ELEMENTS HeaderElements) {
        switch (HeaderElements) {
            case SEGMENT_NUMBER:
                return PacketHeader.get(HEADER_SEGMENT_NUMBER);
            case CHECKSUM:
                return PacketHeader.get(HEADER_CHECKSUM);
            case MODULO_NUMBER:
                return PacketHeader.get(HEADER_MODULO_NUMBER);
            default:
                throw new IllegalArgumentException("Something is broken... bad broken");
        }
    }


    //////////////////////////////PACKAGE DATA METHODS/////////////////////////////

    //SET header key/value pairs
    private void setHeaderValue(HEADER_ELEMENTS HeaderElements, String HeaderValue) {
        switch (HeaderElements) {
            case SEGMENT_NUMBER:
                PacketHeader.put(HEADER_SEGMENT_NUMBER, HeaderValue);
                break;
            case CHECKSUM:
                PacketHeader.put(HEADER_CHECKSUM, HeaderValue);
                break;
            case MODULO_NUMBER:
                PacketHeader.put(HEADER_MODULO_NUMBER, HeaderValue);
                break;
            default:
                throw new IllegalArgumentException("Something is broken... bad broken");
        }
    }

    //gets the packet data at an index
    private byte GETPacketData(int index) {
        if (index >= 0 && index < PackageData.length)
            return PackageData[index];
        throw new IndexOutOfBoundsException(
                "GET PACKET DATA INDEX OUT OF BOUNDS EXCEPTION: index = " + index);
    }

    //get packet data
    byte[] GETPacketData() {
        return PackageData;
    }

    //get packet data size
    int getPacketDataSize() {
        return PackageData.length;
    }


    //Takes an array of bytes to be set as the data segment.
    //If the Packet contains data already, the data is overwritten.
    //Throws IllegalArgumentException if the size of toSet does not
    //conform with the size of the data segment in the packet.
    private void setPacketData(byte[] toSet) throws IllegalArgumentException {
        int argumentSize = toSet.length;
        if (argumentSize > 0) {
            PackageData = new byte[argumentSize];
            System.arraycopy(toSet, 0, PackageData, 0, PackageData.length);
        } else
            throw new IllegalArgumentException(
                    "ILLEGAL ARGUEMENT EXCEPTION-SET PACKET DATA: toSet.length = " + toSet.length);
    }

    //returns packet as a datagram packet
    DatagramPacket getDatagramPacket(InetAddress i, int port) {
        byte[] setData = ByteBuffer.allocate(512)
                .putShort(Short.parseShort(PacketHeader.get(HEADER_SEGMENT_NUMBER)))
                .putShort(Short.parseShort(PacketHeader.get(HEADER_CHECKSUM)))
                .putShort(Short.parseShort(PacketHeader.get(HEADER_MODULO_NUMBER)))
                .put(PackageData)
                .array();

        return new DatagramPacket(setData, setData.length, i, port);
    }

    //declaring enum Header_Elements for key/value pairs
    public enum HEADER_ELEMENTS {
        SEGMENT_NUMBER,
        CHECKSUM,
        MODULO_NUMBER
    }
}
