from socket import *

serverName = gethostbyname(gethostname()) #gets host machine name
serverPort = 12000
bufferSize = 2048

clientSocket = socket(AF_INET, SOCK_DGRAM)
message = raw_input('Input lowercase sentence: ')
clientSocket.sendto(message, (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(bufferSize)

print modifiedMessage
print serverAddress
clientSocket.close()
