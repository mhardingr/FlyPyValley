# GameClient.py

# This class will enable the FlyPyValley game instances to communicate
# with an remote server (set up on machine of choice).


import socket 	# Python module for connecting to other machines

class GameClient(object):
	def __init__(self, hostname, gameComPort):
		self.hostname = hostname
		self.gameComPort = gameComPort

		# Init a socket instance to be able to communicate with server
		self.clientSocket= socket.socket()

		# Init connection data
		self.maxRecieveBytes = 1024

	def initConnection(self):
		maxRecieveBytes = self.maxRecieveBytes
		hostname = self.hostname
		gameComPort = self.gameComPort
		connData = (hostname, gameComPort)
		# Start the connection with remote host with error checking
		try:
			self.clientSocket.connect ( connData )
		except:
			print "Error! Could not connect to the server!"
			return None

		# Initial comms with server will return this socket's PlayerNumber
		# in a string
		dataRecieved = self.clientSocket.recv(maxRecieveBytes)

		playerNumber = -1
		for ch in dataRecieved:
			if (ch.isdigit()):
				playerNumber = eval(ch)

		return playerNumber

	def converseWithServer(self, playerDataList):
		# This method will be run in a while loop in FlyPyValley instance

		# First: send the server playerDataList (turned into a string)
		# Note: the server know which player it is conversing with
		self.clientSocket.send(str(playerDataList))

		# Second, recieve all the player data from server (passed as string)
		maxRecieveBytes = self.maxRecieveBytes
		allPlayerData = self.clientSocket.recv(maxRecieveBytes)

		return allPlayerData

	def closeConnection(self):
		# Need to let the server know that this socket is disconnecting
		closeMsg = "Close"
		self.clientSocket.send(closeMsg)

		self.clientSocket.close()
