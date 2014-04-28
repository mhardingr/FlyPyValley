# SocketPracticeClient.py

import socket

def main():
	# Going to connect to my own machine

	gameClient = socket.socket()		# create socket object
	host = '128.237.68.111'				# Desktop's current IP address
	accessPort = 3210					# gameComsPort = 3210

	gameClient.connect ( (host, accessPort) )
	maxBytesToRecieve = 1024
	print gameClient.recv(maxBytesToRecieve)

	gameClient.close()

main()