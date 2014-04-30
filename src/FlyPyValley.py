# FlyPyValley.py

from OculusCamera import *
from TerrainMesh2 import *	# Version 2 works better!
from MenuWindow import *	# This is used to open a main menu window 

# PyOpenGl modules
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo # Enables use of VBOs

# For random choosing of the heightmap when multiplayer is disabled
import random


class FlyPyValleyGame(object):
	def __init__(self, multiplayerFlag = False):
		self.multiplayerFlag = multiplayerFlag

		# Init list of possible bmp heightmaps to load as terrains
		heightmapNamesList = ["aoneillSpoonValley.bmp", "AtollValley.bmp",
							  "BumpyTerrain.bmp", "CanyonyValley.bmp",
							  "RollingValley.bmp", "BlotchyValley.bmp"]

		selectedHeightmap = None

		# If multiplayer enabled, then use "BlotchyValley.bmp"
		if (multiplayerFlag == True):	
			selectedHeightmap = "BlotchyValley.bmp"
		else:
			selectedHeightmap = random.choice(heightmapNamesList)

		# Save the selectedHeightmap for loading later
		print "Using the %s heightmap!\n\n" % selectedHeightmap
		self.heightmapPath = selectedHeightmap

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
		# ~30 lines of code!

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
			sys.exit()	
		elif (keysym == 'i'):
			# Reset the position of the camera

			###### #BUG, oculus must be re-calibrated not reset
			self.camera.setRotationXYZ(0.0,0.0,0.0)
			self.oculus.setRotationXYZ(0.0,0.0,0.0)

		elif (keysym == "+"):
			OculusCamera.noseToPupilDistance += 0.025	# Manual offset 
			print OculusCamera.noseToPupilDistance
		elif (keysym == "-"):
			OculusCamera.noseToPupilDistance -= .025	# Manual offset 
			print OculusCamera.noseToPupilDistance

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
		self.oculus = OculusCamera(self)
		(initXPos, initYPos, initZPos) = ( 0.0, +220.0, 0.0)
		self.oculus.setWorldCoordinates(initXPos, initYPos, initZPos)
		self.keyStates = {"UP":False, "DOWN":False, "LEFT":False, 
								"RIGHT":False}
		self.timerDelay = 10 # 10 millis, want as many fps as possible
		self.degFOV = 60.0
		self.nearClip = 0.2
		self.farClip = 1000

		# Create TerrainMesh object to load the selectedHeightmap file
		self.valleyMesh = TerrainMesh()
		heightmapRelativePath = "../rsc/" + self.heightmapPath
		# If there is an error in opening the file, close the program
		# AND SOCKETS!######################################
		if (self.valleyMesh.loadHeightmap(heightmapRelativePath) == False):
			print "Error loading heightmap!"
			sys.exit(1)

	def main(self):
		# Output the menu image on a pyglet window instance
		self.displayMenu()	# This will block until a key press

		(self.width, self.height) = (600, 480)
		self.initWorldData()
		if(self.multiplayerFlag == True):
			pass
		self.initGL()

	def displayMenu(self):
		# NOTE: This code will block until a key is pressed!
		gameMenu = MenuWindow()	

myAnimation = FlyPyValleyGame(multiplayerFlag = False)
myAnimation.main() 
