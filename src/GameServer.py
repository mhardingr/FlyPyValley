# GameServer.py

# This code will start up a GameServer object that will:
# 1) Run continuously handling incoming connections from new instances
#  		of the FlyPyValleyGame class.
# 2) Uses threads to be able to handle multiple connections at a time 
# 3) For each connection, the GameServer will first recieve the positional
# 		data from each player (game instance) and save this data. The 
#		GameServer instance will also send (as a string!) out its currently
#		 saved data for all the connected players to all the connected 
#			players (which will accordingly eval(receivedData) to retrieve
#			the copy of the list).
# 4) When a FlyPyValley game instance is closed, its socket will send
# 		a "Close" command, which will trigger the thread running that
#  		connection code to stop running and die.


import socket
import thread

class GameServer(object):
	def __init__(self, hostname, gameComsPort):
		self.hostname = hostname
		self.gameComsPort = gameComsPort

	def initServer(self):
		self.gameServer = socket.socket()	# Creates a socket object
		hostname = self.hostname
		gameComsPort = self.gameComsPort

		# Create the server by binding this socket to this host and port
		self.gameServer.bind( (hostname,gameComsPort) )# Bind to this Port

		self.numPlayersConnected = 0
		self.maxNumPlayers = 4


		# DESCRIBE PROTOCOL for Coms with gameServer:
		# Send str()'s of lists across internet and eval on recieving end
		# Lists from server: [numPlayersConnected, (player1TupleData), 
		# (player2TupleData), (player3TupleData), ((player4TupleData)]
		# When client first connects, it will recv this serverDataList
		# and be assigned a player number, which it will use to parse the data:
		
		# playerTupleData will store (xPos, yPos, zPos)
		self.resetPlayerData = resetPlayerData = (None, None, None)
		self.player1TupleData = resetPlayerData
		self.player2TupleData = resetPlayerData
		self.player3TupleData = resetPlayerData
		self.player4TupleData = resetPlayerData

		self.serverDataList = [self.numPlayersConnected, 
								self.player1TupleData,self.player2TupleData,
								self.player3TupleData,self.player4TupleData]

		maxConnections = 4
		self.gameServer.listen(maxConnections) # Wait for (4 max) connections
		print "Server started! My Address:", hostname

		self.acceptConnections()		# Begin accepting incoming connections
		
	def acceptConnections(self):
		while(True):	# Loop is blocked until server accepts a connection
			# Connect with client
			(intermediate, clientAddr) = self.gameServer.accept() 

			print "Connection made with", clientAddr
			self.numPlayersConnected += 1
			pNum = self.numPlayersConnected # This client's playerNum is saved
			initStr = "New connection! You are player number %d" % pNum
			emptyTuple = ()
			# Send welcome to gameClient with assigned pNum
			intermediate.send(initStr)	

			# Start a new thread to handle this new connection as the
			# while loop is blocked with every gameServer.accept() call
			thread.start_new_thread(lambda: self.handleConnection(pNum,
									 intermediate), emptyTuple)

	def handleConnection(self, playerNum, intermediateSock):
		# Symmetry nec. in recv and send calls:
		# Client code must send first and recv second,
		# while Server code must recv first and send second
		exitFlag = False
		while (exitFlag != True):
			dataRecStr = intermediateSock.recv(1024)
			if (dataRecStr == "Close"):
				exitFlag = True
				self.handlePlayerClose(playerNum)
				continue

			else:
				print dataRecStr
				dataRecList = eval(dataRecStr)
				# Data received is the curr communicating player's posData
				# update playerData
				self.updatePlayerData(playerNum,dataRecList) 
				intermediateSock.send(str(self.serverDataList))
				self.updateServerData()

	def updatePlayerData(self, playerNum, playerCoords):
		# Save the updated playerCoords to playerNum's tupleData
		if (playerNum == 1):
			self.player1TupleData = playerCoords
		elif(playerNum == 2):
			self.player2TupleData = playerCoords
		elif(playerNum == 3):
			self.player3TupleData = playerCoords
		elif(playerNum == 4):
			self.player4TupleData = playerCoords
		else:
			print "Sorry, cannot hold more than 4 players' worth of data!"

	def handlePlayerClose(self, playerNum):
		# Reset the player data for playerNum that just quit
		if (playerNum == 1):
			self.player1TupleData = self.resetPlayerData
		elif (playerNum == 2):
			self.player2TupleData = self.resetPlayerData
		elif (playerNum == 3):
			self.player3TupleData = self.resetPlayerData
		else:
			self.player4TupleData = self.resetPlayerData

		# Player is disconnecting, so decrement numPlayersConnected
		self.numPlayersConnected -= 1
		self.updateServerData()

	def updateServerData(self):
		self.serverDataList = [self.numPlayersConnected, 
								self.player1TupleData, 
								self.player2TupleData,self.player3TupleData,
								self.player4TupleData]


hostIP = '128.237.68.111'
gameComsPort = 3210
myGameServer = GameServer(hostIP,gameComsPort)
myGameServer.initServer()