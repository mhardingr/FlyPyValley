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
		
		# Make sure the clams have left nodes
		self.initVertexDataAndVertexTypeVBOs()

		self.initTexturesAndTextureVBOs()
		self.heightMapImage = None

	def initVertexDataAndVertexTypeVBOs(self):
		# Use lists first then convert to numpy arrays later
		self.grassVertList = []	
		self.groundVertList = []
		self.snowVertList = []
		
		# Using Vertex Buffer Obj. (GPU memory) for increased performance
		self.grassVerticesVBO = None	
		self.groundVerticesVBO = None
		self.snowVerticesVBO = None

	def initTexturesAndTextureVBOs(self):
		self.grassTextureImage = None 
		self.groundTextureImage = None
		self.snowTextureImage = None

		# Init vars to hold vertex texturing data for each type of texture
		# Will convert these lists into numpy arrays later to create VBOs
		self.textureGrassCoords = []
		self.textureGroundCoords = []
		self.textureSnowCoords = []

		# Init pointer variables to Vertex Buffer Objects (GPU memory) 
		self.textureGrassCoordsVBO = None 
		self.textureGroundCoordsVBO = None
		self.textureSnowCoordsVBO = None

		# Saves the texture reference given by GPU 
		self.grassTextureId = None 
		self.groundTextureId = None
		self.snowTextureId = None

	def loadHeightmap( self, mapPath, heightScale= MESH_HEIGHTSCALE, 
							mapResolution = MESH_RESOLUTION):
		
		if (self.openValleyImages(heightmapPath = mapPath) == False):
			print "Program error! Could not open images! Aborting..."
			sys.exit(0)

		# Create a mesh of vertices
		lengthX = self.heightMapImage.size [0]
		widthY = self.heightMapImage.size [1]
		numPixelsPerVertex = 6
		self.numVertices = int ( lengthX * widthY * numPixelsPerVertex 
									/ (mapResolution ** 2) )
		numVertices = self.numVertices

		# Generate (x,y,z) tuples for every vertex in terrain from heightmap
		# as well as texture the terrain with appropriate terrain types 
		# depending on height values
		self.createTerrainFromHeightmap(mapResolution, heightScale)

		self.createTypeVertexListVBOs()
		self.createTextureTypeCoordsVBOs()

		print self.textureGroundCoords[:100]
		print self.groundVertList[:100]

		return True

	def createTypeVertexListVBOs(self):
		# Convert the terrain type vert lists into numpy arrays to
		# pass in to VBO initializer
		grassVertArray = npy.array(self.grassVertList, dtype="f",)	
		groundVertArray = npy.array(self.groundVertList)
		snowVertArray = npy.array(self.snowVertList)

		
		# Using Vertex Buffer Obj. (GPU memory) for increased rendering
		# performance and speed
		self.grassVerticesVBO = vbo.VBO(grassVertArray)	
		self.groundVerticesVBO = vbo.VBO(groundVertArray)
		self.snowVerticesVBO = vbo.VBO(snowVertArray)

	def createTextureTypeCoordsVBOs(self):
		# Save the textureTypeCoordsLists as npy arrays
		textureGrassCoordsArray = npy.array(self.textureGrassCoords)
		textureGroundCoordsArray = npy.array(self.textureGroundCoords)
		textureSnowCoordsArray = npy.array(self.textureSnowCoords)

		print "Creating textureCoords arrays:"
		print textureGroundCoordsArray

		# Create VBOs for textures of each terrain type by passing
		# numpy arrays (made from textureTypeCoords lists) representing 
		self.textureGrassCoordsVBO = vbo.VBO(textureGrassCoordsArray)
		self.textureGroundCoordsVBO = vbo.VBO(textureGroundCoordsArray)
		self.textureSnowCoordsVBO = vbo.VBO(textureSnowCoordsArray)

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

		self.initImageDataRoutine()

	def initImageDataRoutine(self):
		# For grass texture
		# Will save how many vertices have been bound to grass texels
		self.textureGrassCoordIndex = 0	
		self.textureGrassLengthX = self.grassTextureImage.size[0]
		self.textureGrassWidthY = self.grassTextureImage.size[1]
		self.textureGrassCurrX = 0	# Current pixel coords to bind to
		self.textureGrassCurrY = 0
		
		# For ground texture
		# Will save how many vertices have been bound to ground texels
		self.textureGroundCoordIndex = 0	
		self.textureGroundLengthX = self.groundTextureImage.size[0]
		self.textureGroundWidthY = self.groundTextureImage.size[1]
		self.textureGroundCurrX = 0	# Current pixel coords to bind to
		self.textureGroundCurrY = 0

		"""# For snow texture
		# Will save how many vertices have been bound to snow texels
		self.textureSnowCoordIndex = 0	
		self.textureSnowLengthX = self.snowTextureImage.size[0]
		self.textureSnowWidthY = self.snowTextureImage.size[1]
		self.textureSnowCurrX = 0	# Current pixel coords to bind to
		self.textureSnowCurrY = 0"""

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

		# This triangle indexing algorithm adapted from the tutorial:
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

					# Map this vertex to correct type of terrain texture
					self.mapVertexToTerrainTexture(vX = x, height = y, vZ = z)
					"""self.vertList [vertIndex] = (x,y,z)
					self.textureCoords [textIndex] = ((fTerrPosX/lengthX),
														(fTerrPosZ/widthY))
					vertIndex += 1
					textIndex += 1"""

		return True

	def mapVertexToTerrainTexture(self, vX, height, vZ):
		# Height thresholds for each terrain type
		grassLowerThresholdHeight = 0.0	
		groundLowerThresholdHeight = 75.0	
		snowLowerThresholdHeight = 220.0
		maximumHeight = 255.0

		if (grassLowerThresholdHeight <= height <groundLowerThresholdHeight):
			print "Binding to grass texture"
			self.bindVertexToGrassTextureCoord(vX, height, vZ)

		elif (groundLowerThresholdHeight <= height <snowLowerThresholdHeight):
			print "Binding to ground texture"
			self.bindVertexToGroundTextureCoord(vX, height, vZ)
		elif (snowLowerThresholdHeight<= height <= maximumHeight):
			print "Binding to snow texture"
			self.bindVertexToSnowTextureCoord(vX, height, vZ)
		else:
			return False # Invalid height

		return True 	

	def bindVertexToGrassTextureCoord(self, vX, height, vZ):
		currIndex = self.textureGrassCoordIndex
		lengthX = self.textureGrassLengthX
		widthY = self.textureGrassWidthY
		# Bind vertex to grassVertList
		self.grassVertList.append( (vX, height, vZ) )

		# Set the textureGrassRow and Col variables - no range
		self.textureGrassCurrX = texelX = -vX
		self.textureGrassCurrY = texelY = -vZ /2.0

		# Now bind the current texture coordinate with this vertex
		self.textureGrassCoords.append ( (texelX, texelY) )

		# Increment the textureCoord index for next call
		self.textureGrassCoordIndex += 1 

	def bindVertexToGroundTextureCoord(self, vX, height, vZ):
		currIndex = self.textureGroundCoordIndex
		lengthX = self.textureGroundLengthX
		widthY = self.textureGroundWidthY
		# Bind vertex to groundVertList
		self.groundVertList.append( (vX, height, vZ) )

		# Set the textureGroundRow and Col variables - no range
		self.textureGroundCurrX = texelX = -vX
		self.textureGroundCurrY = texelY = -vZ / 2.0
		#(currIndex // widthY)/float(widthY)

		# Now bind the current texture coordinate with this vertex
		self.textureGroundCoords.append ( (texelX, texelY) )

		# Increment the textureCoord index for next call
		self.textureGroundCoordIndex += 1 

	def bindVertexToSnowTextureCoord(self, vX, height, vZ):
		currIndex = self.textureSnowCoordIndex
		lengthX = self.textureSnowLengthX
		widthY = self.textureSnowWidthY
		# Bind vertex to snowVertList
		self.snowVertList.append( (vX, height, vZ) )

		# Set the textureSnowRow and Col variables 
		self.textureSnowCurrX = texelX = -vX
		self.textureSnowCurrY = texelY = -vZ / 2.0

		# Now bind the current texture coordinate with this vertex
		self.textureSnowCoords.append ( (texelX, texelY) )

		# Increment the textureCoord index for next call
		self.textureSnowCoordIndex += 1 

	"""def setColorValueForTextureImage(self, pixelX,heightVal,pixelY):
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
		return """

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

	def drawValleyGround(self):
		groundTextureImg = self.groundTextureImage
		groundTextureId = self.groundTextureId
		numVertices = self.textureGroundCoordIndex - 1 # Len of groundVertList

		# Bind the texture coordinates to this viewport:
		resultId = self.loadTextureToOpenGL(groundTextureImg,groundTextureId)
		# Save the changed textureId
		self.groundTextureId = resultId

		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )	# // Enable Vertex Arrays
		# // Enable Texture Coord Arrays
		#glEnableClientState( GL_TEXTURE_COORD_ARRAY )

		# Bind the Vertex Buffer Objects (VBOs) to graphics card
		# where the ground verts and texture coords will be synced
		self.groundVerticesVBO.bind()
		glVertexPointer(3, GL_FLOAT, 0, None)
		#self.textureGroundCoordsVBO.bind()
		#glTexCoordPointer( 2, GL_FLOAT, 0, None)

		# DRAW THE LANDSCAPE HERE
		glColor3f(0.0, 0.0, 0.0)
		glDrawArrays (GL_TRIANGLES, 0, numVertices)
		
		# Unbind the VBOs here:
		#self.textureGroundCoordsVBO.unbind()
		self.groundVerticesVBO.unbind()

		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )# // Disable Vertex Arrays
		# // Disable Texture Coord Arrays
		#glDisableClientState( GL_TEXTURE_COORD_ARRAY )
		
		# Unload the texture from Opengl:
		self.unloadTextureFromOpenGL()

	def drawValleySnow(self):
		snowTextureImage = self.snowTextureImage
		snowTextureId = self.snowTextureId
		numVertices = self.textureSnowCoordIndex - 1 # Len of snowVertList

		# Bind the texture coordinates to this viewport:
		resultId = self.loadTextureToOpenGL(snowTextureImage, snowTextureId)
		# Save the resulting textureId
		self.snowTextureId = resultId


		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )	# // Enable Vertex Arrays
		# // Enable Texture Coord Arrays
		glEnableClientState( GL_TEXTURE_COORD_ARRAY )

		# Bind the Vertex Buffer Objects (VBOs) to graphics card
		# where the snowVertList and snowTextureCoords will be synced
		self.snowVerticesVBO.bind()
		glVertexPointer(3, GL_FLOAT, 0, None)	# Inits pointers
		self.textureSnowCoordsVBO.bind()
		glTexCoordPointer( 2, GL_FLOAT, 0, None)# Inits pointers

		# DRAW THE LANDSCAPE HERE
		glDrawArrays (GL_TRIANGLES, 0, numVertices)
		
		# Unbind the VBOs here:
		self.textureSnowCoordsVBO.unbind()
		self.snowVerticesVBO.unbind()

		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )# // Disable Vertex Arrays
		# // Disable Texture Coord Arrays
		glDisableClientState( GL_TEXTURE_COORD_ARRAY )
		
		# Unload the texture from Opengl:
		self.unloadTextureFromOpenGL()


	def loadTextureToOpenGL(self, textureImage, textureId):
		lengthX = textureImage.size [0]
		widthY = textureImage.size [1]
		if (textureId == None):
			print "Texture is null!"
			textureId = glGenTextures(1) # GL function to generate Tex pointer
		glBindTexture( GL_TEXTURE_2D, textureId)
		glTexImage2D (GL_TEXTURE_2D,0, 3, lengthX, widthY,0,GL_RGB,
							GL_UNSIGNED_BYTE, 
							textureImage.tostring("raw", "RGB",0,
																-1))
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
		# Allow for texture coords to be mapped from x and z vertcoords
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_REPEAT)

		return textureId

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