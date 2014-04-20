# TerrainMap.py

# My implementation of drawing a 3-D terrain from a given height-map
# Vertex Buffer Object Tutorial code from which this code was (largely) 
# adapted:
# http://nehe.gamedev.net/tutorial/vertex_buffer_objects/22002/

import Struct
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as npy # Need array speed boost

import Image 	# PIL library
import time

class Vertex:
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x= x
		self.y = y
		self.z = z

	def getVertData(self):
		return (self.x,self.y,self.z)

class TextureCoordinates:
	def __init__ (self, u=0.0, v=0.0):
		self.u = u
		self.v = v

	def getTextureCoordsData():
		return (self.u,self.v)

class TerrainMesh:
	# Constants:
	MESH_RESOLUTION = 4.0
	MESH_HEIGHTSCALE = 1.0

	def __init__(self):
		self.numVertices = 0
		
		self.vertList = None
		self.vertListAsString = None

		self.textureCoords = None
		self.textureCoordsAsString = None

		self.textureId = None # Saves the reference given by GPU

		self.heightMapImage = None

	def loadHeightmap( self, mapPath, heightScale=MESH_HEIGHTSCALE,
						 mapResolution = MESH_RESOLUTION):
		# With Error handling, load texture data
		try:
			self.heightMapImage = Image.open(mapPath)
		except:
			print "Error opening file at %s" % (mapPath)
			return False

		# Create a mesh of vertices
		lengthX = self.heightMapImage.size [0]
		widthY = self.heightMapImage.size [1]
		numPixelsPerVertex = 6
		self.numVertices = int ( lengthX * widthY * numPixelsPerVertex 
									/ (mapResolution ** 2) )
		numVertices = self.numVertices

		# Create vertList (3D points) and textureCoords (2D coords)
		# USE NUMPY FOR ARRAY SPEED BOOST - create here array of zeros
		# Use tuple input to describe size and dims of array
		(vertexPointDims, texPointDims) = (1,2)
		initHeight = 0.0

		# CLARIFY: Making a 2d list of height values, where xcoord == row
		# and zcoord == col
		# Iterating over the x-z plane of the given heightmap
		# Number of xCoords:
		numXCoords = lengthX / mapResolution * numPixelsPerVertex ** 0.58   # !
		numZCoords = widthY / mapResolution * numPixelsPerVertex ** 0.58 	# !
		self.vertList = [ [initHeight] * lengthX for zPixel in xrange(widthY) ] 
		self.textureCoords= npy.zeros( (numVertices, texPointDims), 'f')


		### NEEDS OWN method!
		terrPosZ = 0 # Our row variable
		vertIndex = 0
		textIndex = 0
		halfWidthY = widthY / 2.0
		halfLengthX = lengthX / 2.0
		mapResolutionInt = int (mapResolution)
		numTrianglesPerUnitSquare = 6

		# This algorithm is from the tutorial:
		# http://nehe.gamedev.net/tutorial/vertex_buffer_objects/22002/

		for terrPosZ in xrange (0,widthY,mapResolutionInt): # Rows
			for terrPosX in xrange(0,lengthX,mapResolutionInt): # Cols
				for triangle in xrange(numTrianglesPerUnitSquare):
					fTerrPosX = float (terrPosX)
					if (triangle == 1 or triangle == 2 or triangle == 5):
						fTerrPosX += mapResolution
					fTerrPosZ = float (terrPosZ)
					if (triangle == 2 or triangle == 4 or triangle == 5):
						fTerrPosZ += mapResolution

					x = fTerrPosX - halfLengthX
					y=(self.findHeightInHeightmap(int(fTerrPosX),int(terrPosZ))
												* heightScale)
					z = fTerrPosZ - halfWidthY

					self.vertList [terrPosX][terrPosZ] = y
					self.textureCoords [textIndex] = ((fTerrPosX/lengthX),
															(fTerrPosZ/widthY))
					vertIndex += 1
					textIndex += 1

		# Now convert self.vertList to numpy array for easier toString conversion			
		npVertList = npy.array(self.vertList, 'f')
		self.vertListAsString = npVertList.tostring () # Use numpy method
		self.textureCoordsAsString = self.textureCoords.tostring ()

		print self.vertListAsString
		print self.textureCoordsAsString


		self.loadTextureToOpenGL()
		return True 
		

	def loadTextureToOpenGL(self):
		lengthX = self.heightMapImage.size [0]
		widthY = self.heightMapImage.size [1]
		self.textureId = glGenTextures(1)	# Bug was here!!! 
		glBindTexture( GL_TEXTURE_2D, self.textureId)
		glTexImage2D (GL_TEXTURE_2D,0, 3, lengthX, widthY,0,GL_RGB,
							GL_UNSIGNED_BYTE, 
							self.heightMapImage.tostring("raw", "RGB",0,
																-1))
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)

		# Free the texture data
		self.heightMapImage = None
			
	def findHeightInHeightmap( self, pixelX, pixelY):
		# Finds the height at pt (pixelX,pixelY)
		lengthX = self.heightMapImage.size [0]
		widthY = self.heightMapImage.size [1]

		if ((pixelX >= lengthX or pixelX < 0)or(pixelY >=widthY or pixelY<0)):
			return 0
			
		# Note: Image will begin reading at top left of image, but window coords 
		# start at bottom left
		# Here we find RGB components of pixels in heightmap
		adjustedPixelY = widthY - 1 - pixelY
		pixel = self.heightMapImage.getpixel ((pixelX, adjustedPixelY))
		red = float( pixel [0])
		green = float (pixel[1])
		blue = float (pixel[2])
		pixel = self.heightMapImage.getpixel ( (pixelY, pixelX) ) # DK

		# Luminance algorithm: using "grayness" to determine heighth in heightmap
		# Whiter means higher, darker means lower heights
		redLuminance = 0.299
		greenLuminance = 0.587
		blueLuminance = 0.114

		return (redLuminance*red + greenLuminance*green + blueLuminance*blue) 

class Struct : pass

class TerrainMapAnimation(object):
	def keyPressed(self):
		pass

	def reshapeWindow(self, width, height):
		if (height == 0): height = 1

		glViewport(0, 0, width, height) # Reset the curr. viewprt. and persp.transf.
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		fieldOfView = 45.0
		aspectRatio = float(width) / height
		near = 1
		far = 1000.0
		# In order to squash and stretch our objects as resize requires
		gluPerspective(fieldOfView, aspectRatio, near, far)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

	def redrawAll(self):
		# Can do fps here ... (no GLOBALS)
		print "Entered redrawAll!"
		millis = time.clock() * 1000.0
		if (millis - self.prevFPSCheck >= 1000.0):	# one second has passed
			self.prevFPSCheck = time.clock() * 1000.0
			self.numFPS = self.numFrames
			self.numFrames = 0

			#print self.numFPS

		self.numFrames += 1 					# Increment FPS counter
		dRotation = (millis - self.prevTimeDraw) / 1000.0 * 10
		self.prevTimeDraw = millis
		self.flyRot += dRotation

		# Clear screen and depth 
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
		glLoadIdentity()		# Rest the modelview matrix

		# Move the camera
		(camX, camY, camZ)= (0.0, -220.0, 0.0)
		glTranslatef( camX, camY, camZ)	# Make sure above terrain

		glRotatef( 10.0, 1.0, 0.0, 0.0) # look down slightly
		glRotatef( self.flyRot, 0.0, 1.0, 0.0)

		# Enable pointers!
		glEnableClientState( GL_VERTEX_ARRAY)			# Enable vertex arrays
		glEnableClientState( GL_TEXTURE_COORD_ARRAY)	# Enable tex. coord arrays

		print "Pointers enabled!"

		# Using strings way of pointing to arrays!
		glVertexPointer( 3, GL_FLOAT, 0, self.terrainMesh.vertListAsString)
		glTexCoordPointer( 2, GL_FLOAT, 0, self.terrainMesh.textureCoordsAsString)

		print "Vertices pointed to!"
		# Render landscape
		#self.renderLandscape()
		glDrawArrays( GL_TRIANGLES, 0, self.terrainMesh.numVertices)
		print "Array drawn!"
		# Disable Vertex arrays, disable texture coord arrays
		glDisableClientState( GL_VERTEX_ARRAY)		
		glDisableClientState( GL_TEXTURE_COORD_ARRAY) 

		print "Done drawing!"
		glutSwapBuffers()


	# Code for rendering landscape adapted from:
	# https://github.com/soumitrasaxena/TerrainGenerationOpenGL/
	# blob/master/Terrain.cpp
	def renderLandscape(self):
		# Drawing using primitive drawing gl functions and GL_TRIANGLE_STRIP
		# for proper terrain rendering
		numXCoords = len(self.terrainMesh.vertList)
		numZCoords = len(self.terrainMesh.vertList[0])
		glColor3f(1.0, 1.0, 1.0)
		print "Starting to draw:"
		for zPos in xrange(numZCoords - 1):

			glBegin(GL_TRIANGLE_STRIP)
			for xPos in xrange(numXCoords):
				yPos = self.terrainMesh.vertList [xPos][zPos]
				glVertex3f(xPos, yPos, zPos)

				nextZPos = zPos + 1
				nextYPos = self.terrainMesh.vertList [xPos][nextZPos]
				glVertex3f(xPos, nextYPos, nextZPos)
			glEnd()

	def renderObjects(self):
		# Now do rendering: Draw all triangles at once!
		pass

	def initGL (self, width, height):
		# Load the mesh data
		self.terrainMesh = TerrainMesh()
		if (self.terrainMesh.loadHeightmap("../rsc/Terrain.bmp") == False):
			#print "Error loading heightmap!"
			sys.exit(1)

		# Setup GL states
		glClearColor (0.0, 0.0, 0.0, 0.5) 		#Black background
		glClearDepth( 1.0)
		glDepthFunc(GL_LEQUAL)					# Type of Depth testing
		glEnable(GL_DEPTH_TEST)					# Enable depth testing
		glShadeModel(GL_SMOOTH)					# Select smooth shading
		# Most precise perspective calculations
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)  
		glEnable(GL_TEXTURE_2D)					# Enable texturing'
		#glEnable(GL_CULL_FACE)
		#glCullFace(GL_BACK)

		glColor4f (1.0, 6.0, 6.0, 1.0)			# Set coloring color (?)


	def initGLUT (self, width, height):
		glutInit()
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
		glutInitWindowPosition (100, 100)
		glutInitWindowSize(width, height)
		glutCreateWindow("TerrainMap.py!")

		#glutFullScreen()

		# Callbacks / bindings
		glutDisplayFunc( lambda : self.redrawAll())
		glutIdleFunc(lambda: self.redrawAll())
		glutReshapeFunc(lambda width, height: self.reshapeWindow(width,height))
		glutKeyboardFunc(lambda event: self.keyPressed(event))
		glutSpecialFunc(lambda event: self.keyPressed(event)) #For directional keys

	def animationLoop(self, width, height):
		print "Entered animationLoop!"
		self.initGLUT(width, height)
		self.initGL(width, height)
		
		# Enter glut mainloop
		print "Entering main loop!"
		glutMainLoop()

	def runTerrain(self):
		self.flyRot = 0.0
		self.numFPS = 0
		self.numFrames = 0
		self.prevFPSCheck = 0.0
		self.prevTimeDraw = 0.0
		self.terrainMesh = None
		self.winWidth = 600
		self.winHeight = 480
		self.animationLoop(width= self.winWidth, height = self.winHeight)

myAnimation = TerrainMapAnimation()
myAnimation.runTerrain()
