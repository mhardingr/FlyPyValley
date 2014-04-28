# SocketPracticeServer.py

import socket

def main():
	gameServer = socket.socket()	# Creates a socket object
	host = '128.237.68.111' #socket.gethostname()	# Get the name of this machine

	gameComsPort = 3210					# Port to connect to for gameComms

	gameServer.bind( (host,gameComsPort) )# Bind to this Port

	maxConnections = 1
	gameServer.listen(maxConnections) # Wait for connections
	print "Server started! Address:", host
	
	while(True):
		(client, clientAddr) = gameServer.accept() # Connect with client
		print "Connection made with", clientAddr
		client.send("Thank you for connecting")
		client.close()	# Close the connection on client

main()