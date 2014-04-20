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
		self.data = Struct()
		self.data.x= x
		self.data.y = y
		self.data.z = z

	def getVertData(self):
		return (self.data.x,self.data.y,self.data.z)

class TextureCoordinates:
	def __init__ (self, u=0.0, v=0.0):
		self.data = Struct()
		self.data.u = u
		self.data.v = v

	def getTextureCoordsData():
		return (self.data.u,self.data.v)

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
		(vertexPointDims, texPointDims) = (3,2)
		self.vertList = npy.zeros ( (numVertices, vertexPointDims), 'f')
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

					self.vertList [vertIndex] = (x,y,z)
					self.textureCoords [textIndex] = ((fTerrPosX/lengthX),
															(fTerrPosZ/widthY))
					vertIndex += 1
					textIndex += 1
		self.vertListAsString = self.vertList.tostring () # Use numpy method
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

		print (redLuminance*red + greenLuminance*green + blueLuminance*blue) 
		return (redLuminance*red + greenLuminance*green + blueLuminance*blue) 

class Struct : pass

def keyPressed(data):
	pass

def reshapeWindow(data, width, height):
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

def redrawAll(data):
	# Can do fps here ... (no GLOBALS)
	millis = time.clock() * 1000.0
	if (millis - data.prevFPSCheck >= 1000.0):	# one second has passed
		data.prevFPSCheck = time.clock() * 1000.0
		data.numFPS = data.numFrames
		data.numFrames = 0

		#print data.numFPS

	data.numFrames += 1 					# Increment FPS counter
	dRotation = (millis - data.prevTimeDraw) / 1000.0 * 10
	data.prevTimeDraw = millis
	data.flyRot += dRotation

	# Clear screen and depth 
	glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
	glLoadIdentity()		# Rest the modelview matrix

	# Move the camera
	(camX, camY, camZ)= (0.0, -220.0, 0.0)
	glTranslatef( camX, camY, camZ)	# Make sure above terrain

	glRotatef( 10.0, 1.0, 0.0, 0.0) # look down slightly
	glRotatef( data.flyRot, 0.0, 1.0, 0.0)

	# Enable pointers!
	glEnableClientState( GL_VERTEX_ARRAY)			# Enable vertex arrays
	glEnableClientState( GL_TEXTURE_COORD_ARRAY)	# Enable tex. coord arrays


	# Using strings way of pointing to arrays!
	glVertexPointer( 3, GL_FLOAT, 0, data.terrainMesh.vertListAsString)
	glTexCoordPointer( 2, GL_FLOAT, 0, data.terrainMesh.textureCoordsAsString)

	# Render landscape
	glDrawArrays( GL_TRIANGLE_FAN, 0, data.terrainMesh.numVertices)

	# Disable Vertex arrays, disable texture coord arrays
	glDisableClientState( GL_VERTEX_ARRAY)		
	glDisableClientState( GL_TEXTURE_COORD_ARRAY) 

	glutSwapBuffers()

def renderObjects(data):
	# Now do rendering: Draw all triangles at once!
	pass

def initGL (data, width, height):
	# Load the mesh data
	data.terrainMesh = TerrainMesh()
	if (data.terrainMesh.loadHeightmap("../rsc/Terrain.bmp") == False):
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


def initGLUT (data, width, height):
	glutInit()
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	glutInitWindowPosition (100, 100)
	glutInitWindowSize(width, height)
	glutCreateWindow("TerrainMap.py!")

	#glutFullScreen()

	# Callbacks / bindings
	glutDisplayFunc( lambda : redrawAll(data))
	glutIdleFunc(lambda: redrawAll(data))
	glutReshapeFunc(lambda width, height: reshapeWindow(data,width,height))
	glutKeyboardFunc(lambda : keyPressed(data))
	glutSpecialFunc(lambda : keyPressed(data)) #For directional keys

def animationLoop(data, width, height):
	initGLUT(data, width, height)
	initGL(data, width, height)
	
	# Enter glut mainloop
	#print "Entering glutMainLoop"
	glutMainLoop()

def runTerrain():
	data = Struct()
	data.flyRot = 0.0
	data.numFPS = 0
	data.numFrames = 0
	data.prevFPSCheck = 0.0
	data.prevTimeDraw = 0.0
	data.terrainMesh = None
	animationLoop(data, width= 600, height = 480)

runTerrain()
