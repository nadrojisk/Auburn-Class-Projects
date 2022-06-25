import java.io.*;
import java.net.*;

class Class_UDPServer{
  public static void main(String[] args) throws Exception {
      int[] ports = {10028, 10029, 10030, 10031};
      int port = ports[0];

      DatagramSocket serverSocket = new DatagramSocket(port);

      byte[] receiveData = new byte[1024];
      byte[] sendData = new byte[1024];

      System.out.print("Getting IP..."); //remove later
      String localhost = InetAddress.getLocalHost().getHostAddress().trim();  //grabs IP to use for Client
      System.out.println(localhost);
      while(true){
        DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length); //searches for packet to receieve
        serverSocket.receive(receivePacket);
        String sentence = new String(receivePacket.getData());    //gets string from packet

        InetAddress IPAddress = receivePacket.getAddress(); //gets information about client
        int portRecieve = receivePacket.getPort();

        String capitalizedSentence = sentence.toUpperCase();

        sendData = capitalizedSentence.getBytes();

        DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, IPAddress, portRecieve);  //sends data back to client

        serverSocket.send(sendPacket);
      }
  }
}
