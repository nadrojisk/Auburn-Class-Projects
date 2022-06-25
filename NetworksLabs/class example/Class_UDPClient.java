import java.io.*;
import java.net.*;

class Class_UDPClient{
  public static void main(String[] args) throws Exception {
      int[] ports = {10028, 10029, 10030, 10031}; //Group Assigned Port Numbers
      int port = ports[0];  //must be the same as port in server file
      //use tux050 tux065


	  BufferedReader inFromUser = new BufferedReader(new InputStreamReader(System.in)); //create input string
      DatagramSocket clientSocket = new DatagramSocket(); //create client socket

      String localhost = InetAddress.getLocalHost().getHostAddress().trim();
      InetAddress IPAddress = InetAddress.getByName("131.204.14.50"); //translate hostname to IP address using DNS

      byte[] sendData = new byte[1024];
      byte[] receiveData = new byte[1024];

      System.out.print("Please type in message to be converted: "); //remove later

      String sentence = inFromUser.readLine();  //gets user input
      sendData = sentence.getBytes();

      System.out.println("Sending Packet..."); //remove later

      DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, IPAddress, port); //sends user input to server
      clientSocket.send(sendPacket);

      System.out.println("Receiving Packet..."); //remove later

      DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length); //receieves packet from server
      clientSocket.receive(receivePacket);

      String modifiedSentence = new String(receivePacket.getData());  //pulls data from packet
      System.out.println("FROM SERVER: " + modifiedSentence);

      clientSocket.close();
    }
}
