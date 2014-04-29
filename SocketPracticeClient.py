# SocketPracticeClient.py

import socket
import time

def main():
	# Going to connect to my own machine

	gameClient = socket.socket()	# create socket object
	host = '128.237.68.111'			# Desktop's current (static) IP address
	accessPort = 3210				# gameComsPort = 3210

	gameClient.connect ( (host, accessPort) )
	myPlayerNum = -1
	delay = 0.05 # sec
	recCount = 0

	maxBytesToRecieve = 1024
	dataRec = gameClient.recv(maxBytesToRecieve)
	for ch in dataRec:
		if (ch.isdigit()):
			myPlayerNum = eval(ch)
	print dataRec

	for x in xrange(100):
		gameClient.send("Still connected!" + "\t"*myPlayerNum + "hi")
		maxBytesToRecieve = 1024
		dataRec = gameClient.recv(maxBytesToRecieve)
		print myPlayerNum, recCount
		recCount += 1
		time.sleep(delay)


	print "Closing the client"	
	gameClient.send("Close")

	gameClient.close()

main()