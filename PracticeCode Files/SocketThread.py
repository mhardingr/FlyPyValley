# SocketThread.py

import threading.Thread
import Queue.Queue
import socket

class SocketThread (theading.Thread):
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
