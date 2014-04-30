# FlyPyValley.py

from OculusCamera import *	# Handles orientation and movement around world
from TerrainMesh2 import *	# Version 2 works better!
from MenuWindow import *	# This is used to open a main menu window 
from GameClient import *	# Used for multiplayer connection to server

# PyOpenGl modules
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo # Enables use of VBOs

# For random choosing of the heightmap when multiplayer is disabled
import random
# Used when multiplayer is enabled to handle both connection and rendering 
import thread	


class FlyPyValleyGame(object):
	def __init__(self, multiplayerFlag = False):
		self.multiplayerFlag = multiplayerFlag

		(self.width, self.height) = (1600, 900)		# Screen is 1600 X 900

		# Init list of possible bmp heightmaps to load as terrains
		heightmapNamesList = ["aoneillSpoonValley.bmp", "AtollValley.bmp",
							  "BumpyTerrain.bmp", "CanyonyValley.bmp",
							  "RollingValley.bmp", "BlotchyValley.bmp"]

		selectedHeightmap = None

		self.initCameraData()
		self.initAnimationData()

		# If multiplayer enabled, then use "BlotchyValley.bmp"
		#  and init gameClient
		if (multiplayerFlag == True):	
			selectedHeightmap = "BlotchyValley.bmp"
			self.initGameClient()
		else:
			selectedHeightmap = random.choice(heightmapNamesList)

		# Save the selectedHeightmap for loading later
		print "Using the %s heightmap!\n\n" % selectedHeightmap
		self.heightmapPath = selectedHeightmap

	def initCameraData(self):
		# Create an Oculus obj in order to be able to fly around world
		# Starting position well above the rendered terrain
		self.oculus = OculusCamera(self)		
		(initXPos, initYPos, initZPos) = ( 0.0, +220.0, 0.0)
		self.oculus.setWorldCoordinates(initXPos, initYPos, initZPos)
		# Init camera data (field of View ang)
		self.degFOV = 60.0 		# Field of view angle
		self.nearClip = 0.2 	# Don't render objects that are too close
		self.farClip = 1000		# Don't render too distant objects

	def initAnimationData(self):
		# Init a dict to aid in mapping keypresses to T/F values
		self.keyStates = {"UP":False, "DOWN":False, "LEFT":False, 
								"RIGHT":False}
		self.timerDelay = 10 # 10 millis, want as many fps as possible

	def initGameClient(self):

		self.remoteHost = '128.237.68.111'	# IP address of GameServer
		self.gameComPort = 3210				# Arbitrary mutual port number
		self.playerNum = -1
		self.threadExitFlag = False		# Exit condition for comms threads
		# Init game instance's copy of serverData
		self.clientDataList = []	# Will hold [numPlayers, (playerData),...]
		
		# Init GameClient instance
		self.gameClient = GameClient(self.remoteHost, self.gameComPort)

		# Init the game connection
		result = self.gameClient.initConnection()

		if (result != None):
			# Connection achieved! Init comms returned playerNumber
			print "\nConnection achieved! PlayerNum: %d" % result
			self.playerNum = result	
		else:
			# Connection to server failed! Revert to singleplayer
			print "\nConnection failed! Reverting back to singleplayer\n"
			self.multiplayerFlag = False	# Reset multiplayerFlag
			return

		# Start a thread that will run server-client comms alongside
		# rendering of the world until program closes.
		emptyArgsTuple = ()
		thread.start_new_thread(lambda : self.communicateWithGameServer(),
															 emptyArgsTuple)

	def communicateWithGameServer(self):
		# "Endlessly" converse with the server until user decides to
		# close program (pressing ESC)
		while (self.threadExitFlag != True):
			# Send and recieve playerData to the server
			currPlayerDataList = self.oculus.getPositionXYZ()
			result = self.gameClient.converseWithServer(currPlayerDataList)

			# Save the server output in clientData
			self.updateClientDataList(result)

		# Out of the while loop: close the connection!
		print "Closing the connection!!"
		self.gameClient.closeConnection()

	def updateClientDataList(self,result):
		#print result
		self.clientDataList = result

	def animationTimer(self):
		# Update orientation of Oculus!
		self.oculus.updateOrientationRoutine()

		# Handle motion smoothly
		if (self.keyStates["UP"] == True):
			self.oculus.move("FWD") # Move forward if UP key pressed
		elif (self.keyStates["DOWN"] == True):
			self.oculus.move("BACK") # Or move backwards
		if (self.keyStates["LEFT"] == True):
			self.oculus.move("LEFT") # Turn to the left if LEFT key pressed
		elif (self.keyStates["RIGHT"] == True):
			self.oculus.move("RIGHT") # Or turn to the right 


		self.redrawAll()
		glutTimerFunc(self.timerDelay, 
						lambda garbage: self.animationTimer(), None)

	def redrawAll(self):

		self.renderWorld()


	def renderWorld(self):
		# Routine:
		# Clear buffer bits
		# loadIdentity for Projection plane
		# Change perspective (projection mode)
		# loadIdentity for ModelView
		# Draw miscellaneous
		
		# Clear color and depth buffers
		glClearColor(192/255.0, 192/255.0, 192/255.0, 0.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		# Reset projecction matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		############################################################
		gluPerspective(self.degFOV, self.width / float(self.height),
						 self.nearClip, self.farClip)

		# Reset transformations (for ModelView)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		# Prepare the oculus to for drawing the next scene
		self.oculus.updateOrientationRoutine()

		# Apply scene to the left eye first
		glPushMatrix()
		self.oculus.applyLeftEye()

		self.valleyMesh.drawValley()	# Render world!

		glPopMatrix()

		# Apply scene to the right eye next
		glPushMatrix()
		self.oculus.applyRightEye()

		self.valleyMesh.drawValley()	# Render world!

		glPopMatrix()

		glutSwapBuffers()

	def normalKeyEvent(self, eventArgs):	# Handle character events
		escKeyAscii = 27
		keysym = eventArgs[0]
		
		if (keysym == chr(escKeyAscii)): # quit if pressed escape key 
			if (self.multiplayerFlag == True):
				self.threadExitFlag = True # Quit the connection with server!
			self.cleanup()
		elif (keysym == "+"):
			OculusCamera.noseToPupilDistance += 0.025	# Manual offset 
			print "Nose to pupil distance", OculusCamera.noseToPupilDistance
		elif (keysym == "-"):
			OculusCamera.noseToPupilDistance -= .025	# Manual offset 
			print "Nose to pupil distance", OculusCamera.noseToPupilDistance

	def keyUpEventHandler(self, eventArgs):	# Handles the release of arrow key
		keysym = eventArgs[0]
		if (keysym == GLUT_KEY_LEFT):
			self.keyStates["LEFT"] = False
		elif (keysym == GLUT_KEY_RIGHT):
			self.keyStates["RIGHT"] = False
		elif (keysym == GLUT_KEY_DOWN):
			self.keyStates["DOWN"] = False
		elif (keysym == GLUT_KEY_UP):
			self.keyStates["UP"] = False


	def specialKeyEvent(self, eventArgs):	# Handle arrow keys pressed events
		keysym = eventArgs[0]
		# Handle arrow key events
		if (keysym == GLUT_KEY_LEFT):
			self.keyStates["LEFT"] = True
		elif (keysym == GLUT_KEY_RIGHT):
			self.keyStates["RIGHT"] = True
		elif (keysym == GLUT_KEY_DOWN):
			self.keyStates["DOWN"] = True
		elif (keysym == GLUT_KEY_UP):
			self.keyStates["UP"] = True


	def resizeWindow(self, width, height):
		if (height == 0):
			height = 1
		if (width == 0):
			width = 1

		# Update height and width data
		self.width = width
		self.height = height


	def initGL(self):
		
		glutInit()
		glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA | GLUT_ALPHA)
		glutInitWindowPosition(0,0)
		glutInitWindowSize(self.width, self.height)
		glutCreateWindow("FlyPy Valley")
		glViewport(0, 0, self.width, self.height)# Create a viewport for window

		# From TUTNeheHeightmap.py ::::
		# Setup GL States
		glClearColor (192/255.0,192/255.0, 192/255.0, 0.5);# // Grey Background
		glClearDepth (1.0);								   # // Depth Buffer Setup
		glDepthFunc (GL_LEQUAL);						   # // The Type Of Depth Testing
		glEnable (GL_DEPTH_TEST);							# // Enable Depth Testing
		glShadeModel (GL_SMOOTH);							# // Select Smooth Shading
		glEnable(GL_TEXTURE_2D);							# // Enable Texture Mapping
		glHint (GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);	# // Set Perspective Calculations To Most Accurate
		glColor4f (1.0, 6.0, 6.0, 1.0)		


		# Callbacks
		glutDisplayFunc(lambda : self.redrawAll())	# RedrawAll function called
		glutIdleFunc(lambda : self.redrawAll())
		glutReshapeFunc(lambda width, height: self.resizeWindow(width, height))
		glutKeyboardFunc(lambda *eventArgs: self.normalKeyEvent(eventArgs))
		# To handle arrow keys:
		glutSpecialFunc(lambda *eventArgs: self.specialKeyEvent(eventArgs)) 
		glutSpecialUpFunc(lambda *eventArgs: self.keyUpEventHandler(eventArgs))
		# Fullscreen
		glutFullScreen()

		# Call Timer function as with TKinter
		self.animationTimer()

		# mainloop
		glutMainLoop()

	def initWorldData(self):
		# Create TerrainMesh object to load the selectedHeightmap file
		self.valleyMesh = TerrainMesh()
		heightmapRelativePath = "../rsc/" + self.heightmapPath
		# If there is an error in opening the file, close the program
		if (self.valleyMesh.loadHeightmap(heightmapRelativePath) == False):
			print "Error loading heightmap!"
			if (self.multiplayerFlag == True):
				self.threadExitFlag = True 		# Quit the socket connection!
			self.cleanup()				# Cleanup 'main''s thread

	def run(self):
		# Output the menu image on a pyglet window instance
		self.displayMenu()	# This will block until a key press
		self.initWorldData()
		if(self.multiplayerFlag == True):
			pass
		self.initGL()

	def displayMenu(self):
		# NOTE: This code will block until a key is pressed!
		gameMenu = MenuWindow()	


	def cleanup(self):
		glutLeaveMainLoop()		# Kill the animation mainloop

		print "Exiting main program thread"
		return

myAnimation = FlyPyValleyGame(multiplayerFlag = True)
myAnimation.run() 
