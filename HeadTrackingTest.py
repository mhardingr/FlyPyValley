#

# Test mixing controls with mouse (passive) event controls
# and HMD Oculus Orientation tracking to control
# where camera looks


# Adapted from: 
# http://r3dux.org/2011/05/simple-opengl-keyboard-and-mouse-fps-controls/

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import sys
import pyrift	# Python wrapper for OculusSDK
import numpy as np
from math import *
#import NeheHeightmap	# Use terrain generate by tutorial file

class Mouse(object):
	horizontalMoveSensitivity = 200 # Delta mousePosX / degrees of xRotation
	verticalMoveSensitivity = 200 # Delta mousePosY / degrees of yRotation
	def __init__(self, xPos, yPos):
		self.xPos = xPos
		self.yPos = yPos

	def getMouseData(self):
		return (self.xPos, self.yPos)

	def setMouseData(self, newXPos, newYPos):
		self.xPos = newXPos
		self.yPos = newYPos

	def changeCameraAngle(self, camera, newXPos, newYPos):
		deltaHorizontal = newXPos - self.xPos
		deltaVertical = newYPos - self.yPos

		thetaXRot = deltaVertical / Mouse.verticalMoveSensitivity
		thetaYRot = deltaHorizontal / Mouse.horizontalMoveSensitivity

		camera.rotate(thetaXRot, thetaYRot)

	def changeCameraPosition(self, camera ):
		pass

class Camera(object):

	degsPerRadian = 180.0 / pi
	deltaThetaCap = 180 # Max degrees of motion per mouse movement
	def __init__(self, xPos=0.0, yPos=0.0, zPos=1.0, 
					xRot=0.0, yRot=0.0, zRot=0.0):
		self.xPos = xPos
		self.yPos = yPos
		self.zPos = zPos
		self.xRot = xRot
		self.yRot = yRot
		self.zRot = zRot

		# Line of sight vector components: initial values
		self.xLineOfSight = 1.0 /(3**2)
		self.yLineOfSight = 1.0 / (3**2)
		self.zLineOfSight = 1.0 / (3**2)

		self.motionSpeed = 0.5 # world units per frame

	def setRotationXYZ(self, xRot, yRot, zRot):
		self.xRot = xRot
		self.yRot = yRot
		self.zRot = zRot		

	def rotate(self, thetaX, thetaY):
		self.rotateX(thetaX)
		self.rotateY(thetaY)

	def rotateX(self, dTheta):	# UP and DOWN angles
		if (dTheta < Camera.deltaThetaCap):
			self.xRot += dTheta
			if (self.xRot <-90.0):	# Min angle: straight up
				self.xRot = -90.0

			elif (self.xRot >90.0):	# Max angle: straight down
				self.xRot = 90.0

	def rotateY(self, dTheta):	# LEFT or RIGHT angles
		if (dTheta < Camera.deltaThetaCap):
			# Ensure that yRotation is in range -180.0 --> 180.0
			self.yRot += dTheta
			if (self.yRot <-180.0):
				self.yRot += 360.0 	

			elif (self.yRot > 180.0):
				self.yRot -=360.0

	def rotateZ(self, dTheta):	# Clockwise or Coounter (roll) control
		if (dTheta < Camera.deltaThetaCap):
			# Ensure that roll is limited to [-90.0, 90.0] degrees
			self.zRot += dTheta
			if (self.zRot <-90.0):
				self.zRot = -90 	

			elif (self.zRot > 90.0):
				self.zRot = 90.0

	def move(self, dirStr):
		if (dirStr == ""):
			return
		self.updateLineOfSightVectors()
		if (dirStr == "LEFT"):
			self.strafeLeft()
		elif (dirStr == "RIGHT"):
			self.strafeRight()
		elif (dirStr == "FWD"):
			self.moveForward()
		elif (dirStr == "BACK"):
			self.moveBackward()

	def strafeLeft(self):
		# Move orthogonal to the line of sight 

		speed = self.motionSpeed
		dX = -(speed) 
		self.xPos += dX

	def strafeRight(self):
		# Move in the positive X direction
		speed = self.motionSpeed
		dX = +(speed)
		self.xPos += dX

	def moveForward(self):
		# Move along the line of sight vector
		# Add line of sight vector to position vector

		print "Current line of sight vector: <%5f,%5f, %5f>" % (self.xLineOfSight, self.yLineOfSight, self.zLineOfSight)
		speed = self.motionSpeed
		#speed = 1.0
		dX = speed * self.xLineOfSight
		dY = speed * self.yLineOfSight
		dZ = speed * self.zLineOfSight

		self.xPos += dX
		self.yPos += dY
		self.zPos += dZ

	def moveBackward(self):
		# Move along line of sight vector in opposite direction
		# Subtract line of sight vector from position vector
		speed = self.motionSpeed
		dX = -speed * self.xLineOfSight
		dY = -speed * self.yLineOfSight
		dZ = -speed * self.zLineOfSight

		self.xPos += dX
		self.yPos += dY
		self.zPos += dZ

	def cameraUpdateGLRoutine(self):
		# Update line of sight vectors before rendering routine:
		self.updateLineOfSightVectors()

		(refPtX, refPtY, refPtZ) = self.calculateGluReferencePoint()
		#(refPtX, refPtY, refPtZ) = (0.0, 0.0, 0.0)

		# Adjust cameras angle and position
		(xRotMultiplier, yRotMultiplier, zRotMultiplier) = (1.0, 1.0, 1.0)
		glRotatef(self.xRot, xRotMultiplier, 0.0, 0.0)
		glRotatef(self.yRot, 0.0, yRotMultiplier, 0.0)
		glRotatef(self.zRot, 0.0, 0.0, zRotMultiplier)

		# Move the camera to its world coordinates (negative because moving
		# the world in opposite direction)
		glTranslatef(-self.xPos, -self.yPos, -self.zPos)

	def updateLineOfSightVectors(self):
		if (type(self) == OculusCamera):

			print "Updating line of sight vector!: (%3f, %3f,%3f)" % (self.xRot, self.yRot, self.zRot)

		# Convert rotational orientation data into radians
		xRotRads = self.xRot / Camera.degsPerRadian
		yRotRads = self.yRot / Camera.degsPerRadian
		zRotRads = self.zRot / Camera.degsPerRadian

		# To find x component: 
		xCompYaw = sin (yRotRads)	# find x-Component of yaw
		xLineOfSight = xCompYaw

		# To find y component:
		yCompPitch = sin (-xRotRads) # y component of pitch
		yLineOfSight = yCompPitch 

		# To find z component
		# Prioritizing z-component of yaw over that of pitch
		zCompYaw = -cos(yRotRads) # z-component of yaw
		zLineOfSight = zCompYaw 


		# Now normalize lineOfSightComponents to have unit vector for LOS vect
		sqVectorLength = (xLineOfSight**2.0 + yLineOfSight**2.0 
							+ zLineOfSight**2.0)
		sqRootVecLength = sqVectorLength ** 0.5
		normXLineOfSight = xLineOfSight / sqRootVecLength
		normYLineOfSight = yLineOfSight / sqRootVecLength
		normZLineOfSight = zLineOfSight / sqRootVecLength

		# Save the normal components of unit line of sight vector
		self.xLineOfSight = normXLineOfSight
		self.yLineOfSight = normYLineOfSight
		self.zLineOfSight = normZLineOfSight


class OculusCamera(Camera):
	# Stereo Camera implementation
	degsPerRadian = 180.0 / pi
	noseToPupilDistance = 0.047	# Empirical data, in world units
	def __init__(self, world):
		super(OculusCamera, self).__init__()
		
		self.worldData = world
		(winWidth, winHeight) = (world.width, world.height)


		self.eyeFOV = 60 # degrees of FOV
		self.eyeAspectRatio = (winWidth / 2.0) / winHeight

		# GL Perspective data for creating a frustrum in 3-D space
		# Don't render points closer to camera than .2 world units
		self.nearClip = 0.2 
		# Don't render points further than 1000 world units away from camera
		self.farClip = 1000
		pyrift.initialize()	# Inits the Oculus Rift for data retrieval

	def applyRightEye(self):
		(width, height) = (self.worldData.width, self.worldData.height)
		# Prepare right half of screen
		glViewport(width / 2, 0, width / 2, height)

		# Reset Projection and ModelView matrices
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		FOV = self.eyeFOV
		aspectRatio = self.eyeAspectRatio
		near = self.nearClip
		far = self.farClip
		gluPerspective(FOV, aspectRatio, near, far)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()


		# Clear depth buffers
		glClear(GL_DEPTH_BUFFER_BIT)

		# Use Camera class's pre-GLDraw calls method
		# To adjust current camera's angle 
		self.cameraUpdateGLRoutine()

		# Center the frustrum of the right eye some distance away
		# from center of camera (imaginary camera on mid of nose)
		glTranslatef(- OculusCamera.noseToPupilDistance, 0.0, 0.0)

	def applyLeftEye(self):	
		(width, height) = (self.worldData.width, self.worldData.height)
		# Prepare left half of screen
		# Select left half of screen first
		glViewport(0, 0, width / 2, height)	
		
		# Reset Projection and ModelView matrices
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		FOV = self.eyeFOV
		aspectRatio = self.eyeAspectRatio
		near = self.nearClip
		far = self.farClip
		gluPerspective(FOV, aspectRatio, near, far)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		# Clear depth buffers
		glClear(GL_DEPTH_BUFFER_BIT)

		# Use Camera class's pre-GLDraw calls method
		# To adjust current camera's angle 
		self.cameraUpdateGLRoutine()

		# Center the frustrum of the left eye some distance away
		# from center of camera (imaginary camera on mid of nose)
		glTranslatef(+ OculusCamera.noseToPupilDistance, 0.0, 0.0)

	def updateOrientationRoutine(self):
		# (Yaw, pitch, roll) == (yRot, xRot, zRot)
		(yRotRads, xRotRads, zRotRads) = pyrift.get_orientation()
		#print (xRotRads, yRotRads, zRotRads)

		# Empirical tests show that reducing roll by 90% creates a more
		# realistic world tilt
		rollReduceFactor = 0.1
		
		# Convert rotation data to degrees for Opengl functions
		xRotDegs = -xRotRads * OculusCamera.degsPerRadian
		yRotDegs = -yRotRads * OculusCamera.degsPerRadian
		zRotDegs = rollReduceFactor * zRotRads * OculusCamera.degsPerRadian

		self.rotateWorld(xRotDegs, yRotDegs, zRotDegs)

	def rotateWorld(self, newXRot, newYRot, newZRot):
		# Calculate dThetaX, dThetaY, dThetaZ
		dThetaX = newXRot - self.xRot 
		dThetaY = newYRot - self.yRot 
		dThetaZ = newZRot - self.zRot

		# Update camera data using Camera class methods
		self.rotateX(dThetaX)
		self.rotateY(dThetaY)
		self.rotateZ(dThetaZ)


class Animation(object):
	def redrawAll(self):

		self.practiceRender()


	def practiceRender(self):
		# Routine:
		# Clear buffer bits
		# loadIdentity for Projection plane
		# Change perspective (projection mode)
		# loadIdentity for ModelView
		# Draw miscellaneous
		
		# Clear color and depth buffers
		glClearColor(1.0,1.0,1.0,1.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		# Reset projecction matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		self.degFOV = 60.0
		self.nearClip = 0.2
		self.farClip = 1000
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

		self.camera.cameraUpdateGLRoutine()

		# Draw the scene to the left eye
		glColor3f(0.0,178/255.0,200/255.0)
		glutWireTeapot(25.0) # Draw wire cube
		
		glPopMatrix()

		# Apply scene to the right eye next
		glPushMatrix()
		self.oculus.applyRightEye()

		self.camera.cameraUpdateGLRoutine()

		# Draw scene to the right eye
		glColor3f(0.0,178/255.0,200/255.0)
		glutWireTeapot(25.0) # Draw wire cube
		glPopMatrix()

		glutSwapBuffers()

	def drawTerrain(self):

		glLoadIdentity()
		glClearColor(1.0,1.0,1.0,1.0) #Background white
		glColor3f(0.0,178/255.0,255/255.0)
		glBegin(GL_TRIANGLES)
		glVertex3f(-2,-2,-5.0)
		glVertex3f(2,0.0,-5.0)
		glVertex3f(0.0,2,-5.0)
		glEnd()

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

		print "normal Key event handled!"

	def specialKeyEvent(self, eventArgs):	# Handle arrow keys events
		keysym = eventArgs[0]
		# Handle arrow key events
		if (self.oculus != None):
			self.oculus.updateOrientationRoutine()
		if (keysym == GLUT_KEY_LEFT):
			self.oculus.move("LEFT")	# Strafe left
		elif (keysym == GLUT_KEY_RIGHT):
			self.oculus.move("RIGHT")	# Strafe right
		elif (keysym == GLUT_KEY_DOWN):
			self.oculus.move("BACK")	# Move backwards
		elif (keysym == GLUT_KEY_UP):
			self.oculus.move("FWD")		# Move forwards

	def mouseMoved(self, mouseXPos, mouseYPos):
		"""
		if (self.isWarpingPointer == True):
			# glutWarpPointer actually is triggering a mouseMoved event
			# so catch this
			return 

		self.isWarpingPointer = True
		glutWarpPointer(self.middleX, self.middleY)
		self.isWarpingPointer = False
		"""

		print "Mouse moved!:", mouseXPos, mouseYPos
		self.mouse.changeCameraAngle(self.camera, mouseXPos, mouseYPos)

		self.redrawAll()

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
		glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)
		glutInitWindowPosition(0,0)
		glutInitWindowSize(self.width, self.height)
		glutCreateWindow("Headtracking Test")
		glViewport(0, 0, self.width, self.height)# Create a viewport for window

		#Warp mouse to center of screen
		glutWarpPointer(self.middleX, self.middleY)

		# Callbacks
		glutDisplayFunc(lambda : self.redrawAll())	# RedrawAll
		glutIdleFunc(lambda : self.redrawAll())
		glutReshapeFunc(lambda width, height: self.resizeWindow(width, height))
		glutKeyboardFunc(lambda *eventArgs: self.normalKeyEvent(eventArgs))
		# To handle arrow keys:
		glutSpecialFunc(lambda *eventArgs: self.specialKeyEvent(eventArgs)) 
		glutPassiveMotionFunc(lambda mouseX, mouseY: self.mouseMoved(
																mouseX,mouseY))
		# Fullscreen
		#glutFullScreen()

		# mainloop
		glutMainLoop()

	def initWorldData(self):
		self.clicked = False
		self.isWarpingPointer = False
		self.camera = Camera()
		self.oculus = OculusCamera(self)

		(self.middleX, self.middleY) = (self.width / 2, self.height / 2)
		self.mouse = Mouse(self.middleX, self.middleY)

	def main(self):
		(self.width, self.height) = (600, 480)
		self.initWorldData()
		self.initGL()


myAnimation = Animation()
myAnimation.main()