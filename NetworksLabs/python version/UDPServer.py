from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
bufferSize = 2048
serverName = gethostbyname(gethostname()) #gets host machine name



serverSocket.bind(('', serverPort))
print 'The server [%s] is ready to receive:' % serverName 
while 1:
    message, clientAddress = serverSocket.recvfrom(bufferSize)
    if(message != ""):
        print "Received Message: ", message
    modifiedMessage = message.upper()
    serverSocket.sendto(modifiedMessage, clientAddress)
