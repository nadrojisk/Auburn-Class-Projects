import java.io.*;
import java.net.*;

class Class_TCPServer{
  public static void main(String[] args) throws Exception{
    String clientSentence;
    String capitalizedSentence;
    int[] ports = {10028, 10029, 10030, 10031}; //Group Assigned Port Numbers
    int port = ports[0];  //must be the same as port in server file

    //Create welcoming socket at specific port
    ServerSocket welcomeSocket = new ServerSocket(port);

    System.out.print("Getting IP..."); //remove later
    String localhost = InetAddress.getLocalHost().getHostName();//.getHostAddress().trim();  //grabs IP to use for Client
    System.out.println(localhost);

    while(true){
      Socket connectionSocket = welcomeSocket.accept(); //wait on welcoming socket for contact by client

      //create input stream, attached to socket
      BufferedReader inFromClient = new BufferedReader(new InputStreamReader(connectionSocket.getInputStream()));
      //create output stream, attached to socket
      DataOutputStream outToClient = new DataOutputStream(connectionSocket.getOutputStream());
      //read in line from socket
      clientSentence = inFromClient.readLine();

      if(clientSentence != null)  //if message is received print to output
        System.out.println("Receiving message: " + clientSentence);

      //write out line to socket
      capitalizedSentence = clientSentence.toUpperCase() + '\n';

      outToClient.writeBytes(capitalizedSentence);
    }
  }
}
