# TerrainMesh.py

# Class taken from TerrainMap.py

# Heightmap-to-terrain translation algorithms adapted from NEHE tutorial:
# http://nehe.gamedev.net/tutorial/vertex_buffer_objects/22002/

import random		# Used in texturing!
import Image 		# PIL
import numpy as npy		# For creating arrays and improve performance
import OpenGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo # Enables use of VBOs

class TerrainMesh:
	# Constants:
	MESH_RESOLUTION = 4.0
	MESH_HEIGHTSCALE = 1.0

	def __init__(self):
		self.numVertices = 0
		
		self.vertList = None
		# Using Vertex Buffer Obj. (GPU memory) for increased performance
		self.verticesVBO = None		

		self.textureGrassImage = None 
		self.textureGroundImage = None
		self.textureSnowImage = None

		# Init vars to hold vertex texturing data for each type of texture
		self.textureGrassVertexCoords = None
		self.textureGroundVertexCoords = None
		self.textureSnowVertexCoords = None

		# Init pointer variables to Vertex Buffer Objects (GPU memory) 
		self.textureGrassCoordsVBO = None 
		self.textureGroundCoordsVBO = None
		self.textureSnowCoordsVBO = None

		# Saves the texture reference given by GPU 
		self.textureGrassId = None 
		self.textureGroundId = None
		self.textureSnowId = None

		self.heightMapImage = None

	def loadHeightmap( self, mapPath, heightScale= MESH_HEIGHTSCALE, 
							mapResolution = MESH_RESOLUTION):
		
		if (self.openValleyImages(heightmapPath = mapPath) == False):
			print "System error! Could not open images! Aborting..."
			sys.exit(0)

		# Create a mesh of vertices
		lengthX = self.heightMapImage.size [0]
		widthY = self.heightMapImage.size [1]
		numPixelsPerVertex = 6
		self.numVertices = int ( lengthX * widthY * numPixelsPerVertex 
									/ (mapResolution ** 2) )
		numVertices = self.numVertices

		# Initialize the textureImage using the same dim.s as heightmap
		self.textureImage = Image.new("RGB", size=(widthY,lengthX))

		# Create vertList (3D points) and textureCoords (2D coords)
		# USE NUMPY FOR ARRAY SPEED BOOST - create here array of zeros
		# Use tuple input to describe size and dims of array
		(vertexPointDims, texPointDims) = (3,2)

		self.vertList = npy.zeros ( (numVertices, vertexPointDims), 'f') 
		self.textureCoords= npy.zeros( (numVertices, texPointDims), 'f')

		# Generate (x,y,z) tuples for every vertex in terrain from heightmap
		self.createTerrainFromHeightmap(mapResolution, heightScale)

		# Update VBOs:
		self.verticesVBO = vbo.VBO(self.vertList)
		self.textureCoordsVBO = vbo.VBO(self.textureCoords)

		assert(self.loadTextureToOpenGL() == True)
		return True 

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
			self.textureGrassImage = Image.open(self.grassImagePath)
		except:
			print "Error opening file at %s" % (self.grassImagePath)
			return False

		# With Error handling, load ground texture image
		try:
			self.textureGroundImage = Image.open(self.groundImagePath)
		except:
			print "Error opening file at %s" % (self.groundImagePath)
			return False

		"""# With Error handling, load snow texture image
		try:
			self.textureSnowImage = Image.open(self.snowImagePath)
		except:
			print "Error opening file at %s" % (self.snowImagePath)
			return False
		return True # Successfully opened file paths"""
		
	def createTerrainFromHeightmap(self, mapResolution, heightScale):
		## NEED TO CUT DOWN ON LENGTH HERE
		
		lengthX = self.heightMapImage.size [0]
		widthY = self.heightMapImage.size [1]
		terrPosZ = 0 # Our row variable
		vertIndex = 0
		textIndex = 0
		halfWidthY = widthY / 2.0
		halfLengthX = lengthX / 2.0
		mapResolutionInt = int (mapResolution)
		numTrianglesPerUnitSquare = 6

		# This algorithm is translated from the tutorial:
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
					
					(x, z) = (fTerrPosX - halfLengthX, fTerrPosZ - halfWidthY)
					(texPixelX,texPixelZ) = (int(fTerrPosX),int(fTerrPosZ))
					y=(self.findHeightInHeightmap(texPixelX,texPixelZ)
													*heightScale)

					# Using a separate image for texturing: 
					# Color in color based on height of this current vertice
					self.setColorValueForTextureImage(texPixelX,y,texPixelZ)
					self.vertList [vertIndex] = (x,y,z)
					self.textureCoords [textIndex] = ((fTerrPosX/lengthX),
														(fTerrPosZ/widthY))
					vertIndex += 1
					textIndex += 1

		return True

	def setColorValueForTextureImage(self, pixelX,heightVal,pixelY):
		lengthX = self.textureImage.size[0]
		widthY = self.textureImage.size[1]
		# Note: Image will begin reading at top left of image, but window coords 
		# start at bottom left
		# Here we find RGB components of pixels in heightmap
		adjustedPixelY = widthY - 1 - pixelY

		dirs = [(-2,-2), (-2,-1), (-2,0), (-2, +1), (-2,+2),
				(-1,-2), (-1,-1), (-1,0), (-1,+1),  (-1,+2),
				(0,-2), (0,-1), (0,0), (0,+1),  (0,+2),
				(+1,-2), (+1,-1), (+1,0), (+1,+1),  (+1,+2),
				(+2,-2), (+2,-1), (+2,0), (+2,+1),  (+2,+2)]

		textureColorAtPixel = self.selectColorFromHeightValue(heightVal)
		# Extrapolate chosen color to 9 pixel-area
		for currDir in dirs:	
			(dX, dY) = currDir
			(currPixelX, currPixelY) = (pixelX+dX, adjustedPixelY + dY)
			if ((currPixelX <0 or currPixelY<0)
					 or (currPixelX>= lengthX or currPixelY>=widthY)):
				continue	# If pixels out of range, try next direction
			currentPixel = (currPixelX, currPixelY)
			self.textureImage.putpixel(currentPixel, textureColorAtPixel)
		return 

	"""def selectColorFromHeightValue(self, heightVal):
		# Our color palette:
		dirtBlack = (0, 0, 0)
		rockGray = (169, 169, 169)	# Dark gray
		valleyGreen = (107, 142, 35)# Olive drab
		snowWhite = (250, 250, 240)# Floral white
		# Constants
		(maxHeight, minHeight, terrFactor) = (255.0, 0.0, 0)
		(groundFloor, grassRockBound, rockSnowBound) = (0.0, 100.0, 200.0)
		selectedColor = None
		colorPossibilities = list()
		if (groundFloor <= heightVal <= grassRockBound):
			terrFactor = (heightVal - groundFloor) / (grassRockBound)
			colorPossibilities = [valleyGreen, rockGray]
		elif (grassRockBound < heightVal <= rockSnowBound):
			terrFactor =((heightVal-grassRockBound) 
								/ (rockSnowBound-grassRockBound))
			colorPossibilities = [rockGray, valleyGreen]
		else:
			terrainFactor = 0.0	# Want to assure only snow is present at caps
			colorPossibilities = [snowWhite]		

		colorChoice = random.randint(0,1) *terrFactor
		return colorPossibilities[int(round(colorChoice)) ]"""

	def loadTextureToOpenGL(self):
		lengthX = self.heightMapImage.size [0]
		widthY = self.heightMapImage.size [1]
		if (self.textureId == None):
			self.textureId = glGenTextures(1)	# Bug was here!!! 
		glBindTexture( GL_TEXTURE_2D, self.textureId)
		glTexImage2D (GL_TEXTURE_2D,0, 3, lengthX, widthY,0,GL_RGB,
							GL_UNSIGNED_BYTE, 
							self.textureImage.tostring("raw", "RGB",0,
																-1))
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)

		return True

	def unloadTextureFromOpenGL(self):
		glBindTexture(GL_TEXTURE_2D, 0)
			
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
		pixel = self.heightMapImage.getpixel ( (pixelY, pixelX) ) 

		# Adapted from NeheTutorial file:
		# Luminance algorithm: using "grayness" to determine heighth in heightmap
		# Whiter means higher, darker means lower heights
		redLuminance = 0.299
		greenLuminance = 0.587
		blueLuminance = 0.114

		return (redLuminance*red + greenLuminance*green + blueLuminance*blue) 