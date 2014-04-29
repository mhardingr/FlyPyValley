# SocketPracticeServer.py

import socket
import threading
import thread

class SocketHandlingThread (threading.Thread):
	def __init__(self):
		super(SocketThread,self).__init__()
		self.accessPort = 3210
		self.host = '128.237.68.111'	# Static IP for Desktop

		self.clientSock = socket.socket()
		self.exit = False
		self.taskQueue = Queue.Queue() 

		self.initSocket()

	def initSocket(self):
		self.clientSock.connect( (self.host, self.accesPort) )
	
	def run(self):
		# TODO: whatever WHILE LOOP
		"""
		while (self.exit != True):
			BLA


		"""
		pass

	def stop(self):
		self.exit = True

		# To call in main program
		# s = SocketThread()
		# s.start()

		# When exit program, call s.stop()

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
		
		# playerTupleData will store (xPos, yPos, zPos, xRot, yRot, zRot)
		self.resetPlayerData = resetPlayerData = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
		self.player1TupleData = resetPlayerData
		self.player2TupleData = resetPlayerData
		self.player3TupleData = resetPlayerData
		self.player4TupleData = resetPlayerData

		self.serverDataList = [self.numPlayersConnected, 
								self.player1TupleData, 
								self.player2TupleData,self.player3TupleData,
								self.player4TupleData]

		maxConnections = 4
		self.gameServer.listen(maxConnections) # Wait for (4 max) connections
		print "Server started! Address:", hostname

		self.acceptConnections()		# Begin accepting incoming connections
		
	def acceptConnections(self):
		while(True):	# Loop is blocked until server accepts a connection
			# Connect with client
			(intermediate, clientAddr) = self.gameServer.accept() 
			# Start a new thread to handle/communcate with client


			print "Connection made with", clientAddr
			self.numPlayersConnected += 1
			initStr = "Thank you for connecting, you are player number %d" % self.numPlayersConnected
			currPlayer = self.numPlayersConnected
			emptyTuple = ()
			intermediate.send(initStr)
			thread.start_new_thread(lambda: self.handleConnection(currPlayer,
									 intermediate), emptyTuple)

	def handleConnection(self, playerNum, intermediateSock):
		# Symmetry nec. in recv and send calls:
		# Client code must send first and recv second,
		# while Server code must recv first and send second
		exitFlag = False
		while (exitFlag != True):
			dataRec = intermediateSock.recv(1024)
			print dataRec 
			intermediateSock.send(str(self.serverDataList))
			if (dataRec == "Close"):
				exitFlag = True
				self.handlePlayerClose(playerNum)
			self.updateServerData()

	def handlePlayerClose(self, playerNum):
		if (playerNum == 1):
			self.player1TupleData = self.resetPlayerData
		elif (playerNum == 2):
			self.player2TupleData = self.resetPlayerData
		elif (playerNum == 3):
			self.player3TupleData = self.resetPlayerData
		else:
			self.player4TupleData = self.resetPlayerData
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