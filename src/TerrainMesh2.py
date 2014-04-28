# TerrainMesh2.py

# My implementation of drawing a 3-D terrain from a given height-map
# Vertex Buffer Object Tutorial code from which this code was (largely) 
# adapted:
# http://nehe.gamedev.net/tutorial/vertex_buffer_objects/22002/

import Struct
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo # Enables use of VBOs


import numpy as npy # Need array speed boost

import Image 	# PIL library
import time


class TerrainMesh:
	# Constants:
	MESH_RESOLUTION = 4.0
	MESH_HEIGHTSCALE = 1.0

	def __init__(self):
		self.numVertices = 0

		self.vertList = None
		self.vertListAsString = None
		self.verticesVBO = None		# Using VBOs

		self.textureCoords = None
		self.textureCoordsAsString = None
		self.textureCoordsVBO = None # Using VBOs

		self.textureId = None # Saves the reference given by GPU

		self.heightMapImage = None

	def openValleyImages(self, heightmapPath):
		self.grassImagePath = "../rsc/seamlesslonggreengrass.bmp"
		self.groundImagePath = "../rsc/seamlessmixedgroundcover.bmp"
		self.snowImagePath = "../rsc/snowtexture.bmp"

		# With Error handling, load heightmap image
		try:
			self.heightMapImage = Image.open(heightmapPath)
		except:
			print "Error opening file at %s" % (mapPath)
			return False

		# With Error handling, load grass texture image
		try:
			self.grassTextureImage = Image.open(self.grassImagePath)
		except:
			print "Error opening file at %s" % (self.grassImagePath)
			return False

		# With Error handling, load ground texture image
		try:
			self.groundTextureImage = Image.open(self.groundImagePath)
		except:
			print "Error opening file at %s" % (self.groundImagePath)
			return False

		"""# With Error handling, load snow texture image
		try:
			self.snowTextureImage = Image.open(self.snowImagePath)
		except:
			print "Error opening file at %s" % (self.snowImagePath)
			return False
		return True # Successfully opened file paths"""

	def loadHeightmap( self, mapPath):

		if (self.openValleyImages(heightmapPath = mapPath) == False):
			print "Program error! Could not open images! Aborting..."
			sys.exit(0)

		heightScale= self.MESH_HEIGHTSCALE
		mapResolution = self.MESH_RESOLUTION

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
		initHeight = 0.0

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

		# Now convert self.vertList to numpy array for easier toString conversion
		self.vertListAsString = self.vertList.tostring () # Use numpy method
		self.textureCoordsAsString = self.textureCoords.tostring ()

		# Update VBOs:
		self.verticesVBO = vbo.VBO(self.vertList)
		self.textureCoordsVBO = vbo.VBO(self.textureCoords)


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
	
	def drawValley(self):

		self.drawValleyGrass()

		self.drawValleyGround()

		################self.drawValleySnow()


	def drawValleyGrass(self):
		grassTextureImage = self.grassTextureImage
		grassTextureId = self.grassTextureId
		numVertices = self.textureGrassCoordIndex- 1 # Number of verts in list

		# Bind the texture coordinates to screen ( a viewport ):
		resultId = self.loadTextureToOpenGL(grassTextureImage, grassTextureId)
		# Save the resulting textureId
		self.grassTextureId = resultId

		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )	# // Enable Vertex Arrays
		# // Enable Texture Coord Arrays
		glEnableClientState( GL_TEXTURE_COORD_ARRAY )	

		# Bind the Vertex Buffer Objects (VBOs) to graphics card
		# Grass verts and texturecoords are synchronized on the card
		self.grassVerticesVBO.bind()
		glVertexPointer(3, GL_FLOAT, 0, None)	# Inits the pointer in GPU
		self.textureGrassCoordsVBO.bind()
		glTexCoordPointer( 2, GL_FLOAT, 0, None)# Inits the pointer in GPU

		# DRAW THE LANDSCAPE HERE
		glDrawArrays (GL_TRIANGLES, 0, numVertices)
		
		# Unbind the VBOs here:
		self.textureGrassCoordsVBO.unbind()
		self.grassVerticesVBO.unbind()

		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )# // Disable Vertex Arrays
		# // Disable Texture Coord Arrays
		glDisableClientState( GL_TEXTURE_COORD_ARRAY )	
		
		# Unload the texture from Opengl:
		self.unloadTextureFromOpenGL() 