# OculusCamera.py

# A wrapper for OculusRift using the camera class
# Handles the orientation and appropriate rotation of world
# using Oculus device's orientation in conjunction with arrow keys component

from math import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Camera import *
import pyrift


class OculusCamera(Camera):
	# Stereo Camera implementation
	degsPerRadian = 180.0 / pi
	noseToPupilDistance = 3.6973	# Empirical data, in world units
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

		# Empirical tests show that reducing roll by 95% creates a more
		# realistic world tilt
		rollReduceFactor = 0.2
		
		# Convert rotation data to degrees for Opengl functions
		xRotDegs = -xRotRads * OculusCamera.degsPerRadian
		yRotDegs = -yRotRads * OculusCamera.degsPerRadian
		zRotDegs = rollReduceFactor * zRotRads * OculusCamera.degsPerRadian

		self.rotateWorld(xRotDegs, yRotDegs, zRotDegs)

	def rotateWorld(self, newXRot, newYRot, newZRot):
		orientatingXRotOffset = self.orientatingXRotOffset
		orientatingYRotOffset = self.orientatingYRotOffset
		orientatingZRotOffset = self.orientatingZRotOffset

		# Update camera data using Camera class methods
		self.setRotationXYZ(newXRot, newYRot, newZRot)

		# Then rotate the scene even more by adding the orientat. angle 
		# offsets. (Use Camera methods in order to control outputed angles)
		self.rotateX(orientatingXRotOffset)
		self.rotateY(orientatingYRotOffset)
		self.rotateZ(orientatingZRotOffset)
