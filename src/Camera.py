# Camera.py
# Author: Matthew Harding

# Code to control the generic OpenGL perspective-controlling camera
# for 3-D environments.


from math import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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

		# Initialize "orientation" offsets (offset angles added using arrow 
		# keys)
		self.orientatingXRotOffset = 0.0
		self.orientatingYRotOffset = 0.0
		self.orientatingZRotOffset = 0.0

		# Line of sight vector components: initial values
		self.xLineOfSight = 1.0 /(3**2)
		self.yLineOfSight = 1.0 / (3**2)
		self.zLineOfSight = 1.0 / (3**2)

		self.motionSpeed = 0.5 # world units per frame

	def setRotationXYZ(self, xRot, yRot, zRot):
		self.xRot = xRot
		self.yRot = yRot
		self.zRot = zRot		

	def rotate2D(self, thetaX, thetaY):
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
			self.turnLeft()
		elif (dirStr == "RIGHT"):
			self.turnRight()
		elif (dirStr == "FWD"):
			self.moveForward()
		elif (dirStr == "BACK"):
			self.moveBackward()

	def turnLeft(self):
		# To turn "left" theta degrees from current line of sight
		dTheta = -2.0 # degrees
		dThetaRads = dTheta / Camera.degsPerRadian
		xRotRads = self.xRot / Camera.degsPerRadian
		yRotRads = self.yRot / Camera.degsPerRadian

		# Must find xRotComponent and yRotComponent rotations for left turn
		# First calculate x and y components of new vector (vector P):
		# P = lineOfSightVector * cos(dthetaRads)
		
		# Need to use cosine and sine product trigonmetric identities
		xCompOfNewLOSVector = 1 / 2.0 * (cos(yRotRads - dThetaRads) + 
											cos(yRotRads+dThetaRads))
		newYRotInRads = acos (xCompOfNewLOSVector)

		yCompOfNewLOSVector = 1 / 2.0 * (sin(-xRotRads - dThetaRads) +
											sin(-xRotRads+dThetaRads))
		newXRotInRads = - asin(yCompOfNewLOSVector)

		# Save actual values of xRotOffset and yRotOffset
		actualXRotOffset = newXRotInRads - xRotRads
		actualYRotOffset = newYRotInRads - yRotRads

		#self.orientatingXRotOffset += actualXRotOffset * Camera.degsPerRadian
		#self.orientatingYRotOffset += actualYRotOffset * Camera.degsPerRadian
		self.orientatingYRotOffset += dTheta


		#self.xRot = newXRotInRads / Camera.degsPerRadian
		self.yRot = newYRotInRads / Camera.degsPerRadian

		#"""
		self.yRot += dTheta



	def turnRight(self):
		# To turn "right" theta degrees from the current line of sight vector
		dTheta = +2.0 # degrees
		self.orientatingYRotOffset += dTheta

		self.yRot += dTheta


	def moveForward(self):
		# Move along the line of sight vector
		# Add line of sight vector to position vector
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

		# Adjust cameras angle and position
		(xRotMultiplier, yRotMultiplier, zRotMultiplier) = (1.0, 1.0, 1.0)
		glRotatef(self.xRot, xRotMultiplier, 0.0, 0.0)
		glRotatef(self.yRot, 0.0, yRotMultiplier, 0.0)
		glRotatef(self.zRot, 0.0, 0.0, zRotMultiplier)

		# Move the camera to its world coordinates (negative because moving
		# the world in opposite direction)
		glTranslatef(-self.xPos, -self.yPos, -self.zPos)

	def updateLineOfSightVectors(self):
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