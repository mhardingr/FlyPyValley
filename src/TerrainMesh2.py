# TerrainMesh2.py

# My implementation of drawing a 3-D terrain from a given height-map
# Vertex Buffer Object Tutorial code from which this code was (largely) 
# adapted:
# http://nehe.gamedev.net/tutorial/vertex_buffer_objects/22002/

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
		self.verticesVBO = None		# Using VBOs

		self.colorCoords = None
		self.colorCoordsVBO = None # Using VBOs

		self.heightMapImage = None

		# Save the terrain type colors (grass, grass-dirt mix, etc.)
		self.meadowRGB = (0,92,9)
		self.grassBladeRGB = (0,153,0)
		self.siennaBrownRGB = (142, 107, 35)
		self.burlyWoodRGB = (255, 211, 155)
		self.snowWhiteRGB = (245, 245, 245)
		self.pureSnowWhiteRGB = (255, 255, 255)
		self.maxColorCompVal = 255.0

	def loadHeightmap( self, mapPath):

		# With Error handling, load heightmap image
		try:
			self.heightMapImage = Image.open(mapPath)
		except:
			print "Error opening file at %s" % (mapPath)
			return False

		heightScale= float(self.MESH_HEIGHTSCALE)
		mapResolution = float(self.MESH_RESOLUTION)

		# Create a mesh of vertices
		self.imLengthX = self.heightMapImage.size [0]
		self.imWidthY = self.heightMapImage.size [1]
		numPixelsPerVertex = 6
		self.numVertices = int ( self.imLengthX * self.imWidthY 
								* numPixelsPerVertex / (mapResolution ** 2) )
		numVertices = self.numVertices

		# Create vertList (3D points) and textureCoords (2D coords)
		# USE NUMPY FOR ARRAY SPEED BOOST - create here array of zeros
		# Use tuple input to describe size and dims of array
		(vertexPointDims, colorPointDims) = (3,3)

		self.vertList = npy.zeros ( (numVertices, vertexPointDims), 'f') 
		self.colorCoords= npy.zeros( (numVertices, colorPointDims), 'f')

		self.createTerrainFromHeightmap(heightScale, mapResolution)

		self.initVertexAndColorVBOs()

		return True 

	def initVertexAndColorVBOs(self):
		# Update VBOs:
		self.verticesVBO = vbo.VBO(self.vertList)
		self.colorCoordsVBO = vbo.VBO(self.colorCoords)

	def createTerrainFromHeightmap(self, heightScale, mapResolution):
		### NEEDS OWN method!
		terrPosZ = 0 # Our row variable
		vertIndex = 0
		colorIndex = 0
		halfWidthY = self.imWidthY / 2.0
		halfLengthX = self.imLengthX / 2.0
		mapResolutionInt = int (mapResolution)
		numTrianglesPerUnitSquare = 6

		# This algorithm is from the tutorial:
		# http://nehe.gamedev.net/tutorial/vertex_buffer_objects/22002/

		for terrPosZ in xrange (0,self.imWidthY,mapResolutionInt): # Rows
			for terrPosX in xrange(0,self.imLengthX,mapResolutionInt): # Cols
				for triangle in xrange(numTrianglesPerUnitSquare):
					fTerrPosX = float (terrPosX)
					if (triangle == 1 or triangle == 2 or triangle == 5):
						fTerrPosX += mapResolution
					fTerrPosZ = float (terrPosZ)
					if (triangle == 2 or triangle == 4 or triangle == 5):
						fTerrPosZ += mapResolution

					x = fTerrPosX - halfLengthX
					y=(self.findHeightInHeightmap(int(fTerrPosX),int(fTerrPosZ))
												* heightScale)
					z = fTerrPosZ - halfWidthY

					self.vertList [vertIndex] = (x,y,z)
					self.setVertexColorFromHeightValueAt(colorIndex, height=y)

					vertIndex += 1
					colorIndex += 1

		self.initVertexAndColorVBOs()


	def setVertexColorFromHeightValueAt(self, currIndex, height):
		# Depending on this vertex's height in the world, we will assign
		# it a certain color (grass shades for lowland, dirt shades for midland,
		# and snow for highlands):

		self.meadowGreenMinHeight = 0
		self.grassBladeMinHeight = 70
		self.siennaBrownMinHeight = 100
		self.burlyWoodMinHeight = 150
		self.snowWhiteMinHeight = 170
		self.pureWhiteSnowMinHeight = 220

		selColor = (0,0,0)
		if (self.meadowGreenMinHeight<=height<self.grassBladeMinHeight):
			selColor = self.mapColorGrassGrassGradient(height)
		elif(self.grassBladeMinHeight<=height<self.siennaBrownMinHeight):
			selColor = self.mapColorGrassDirtGradient(height)
		elif(self.siennaBrownMinHeight<=height<self.burlyWoodMinHeight):
			selColor = self.mapColorDirtDirtGradient(height)
		elif(self.burlyWoodMinHeight<=height<self.snowWhiteMinHeight):
			selColor= self.mapColorDirtSnowGradient(height)
		elif(self.snowWhiteMinHeight<=height):
			selColor = self.mapColorSnowSnowGradient(height)
		
		# Limit the RGB values between 0 and 255/255
		# Must be RGB in range [0.0,1.0]
		selColor = self.restrictRGBValue(*selColor)

		self.colorCoords [currIndex] = selColor	
	
	def mapColorGrassGrassGradient(self, vertHeight):
		# Calculate color by weighted average of colors at boundaries
		# weights determined by closeness of vertHeight to each bound

		meadowMinHeight = self.meadowGreenMinHeight
		grassBladeMinHeight = self.grassBladeMinHeight
	
		meadowRGB = self.meadowRGB
		grassBladeRGB = self.grassBladeRGB

		maxColorFactor = self.findMaxColorGradientFactor(meadowMinHeight,
														 grassBladeMinHeight,
														 vertHeight)
		minColorFactor = 1.0 - maxColorFactor		


		# Calculate the RGB values of selRGB
		selectedColRed = int (meadowRGB[0]*minColorFactor + 
									grassBladeRGB[0]*maxColorFactor)
		selectedColGreen = int (meadowRGB[1]*minColorFactor + 
								grassBladeRGB[1]*maxColorFactor)
		selectedColBlue = int (meadowRGB[2]*minColorFactor +
								grassBladeRGB[2]*maxColorFactor)

		return  (selectedColRed, selectedColGreen, selectedColBlue)

	def mapColorGrassDirtGradient(self, vertHeight):
		# Calculate color by weighted average of min and maxColors
		# for this region of terrain.

		grassBladeMinHeight = self.grassBladeMinHeight
		siennaBrownMinHeight = self.siennaBrownMinHeight

		grassBladeRGB = self.grassBladeRGB
		siennaBrownRGB = self.siennaBrownRGB

		maxColorFactor = self.findMaxColorGradientFactor(grassBladeMinHeight,
														 siennaBrownMinHeight,
														 vertHeight)
		minColorFactor = 1.0 - maxColorFactor

		# Calculate the RGB values of selRGB
		selectedColRed = int (grassBladeRGB[0]*minColorFactor + 
								siennaBrownRGB[0]*maxColorFactor)
		selectedColGreen = int (grassBladeRGB[1]*minColorFactor + 
								siennaBrownRGB[1]*maxColorFactor)
		selectedColBlue = int (grassBladeRGB[2]*minColorFactor +
								siennaBrownRGB[2]*maxColorFactor)

		return  (selectedColRed, selectedColGreen, selectedColBlue)

	def mapColorDirtDirtGradient(self, vertHeight):
		# Calculate color by weighted average of min and maxColors
		# for this region of terrain.

		siennaBrownMinHeight = self.siennaBrownMinHeight
		burlyWoodMinHeight = self.burlyWoodMinHeight


		siennaBrownRGB = self.siennaBrownRGB
		burlyWoodRGB = self.burlyWoodRGB

		# Find gradient ratios/ weights of max and min colors
		maxColorFactor = self.findMaxColorGradientFactor(siennaBrownMinHeight,
														 burlyWoodMinHeight,
														 vertHeight)
		minColorFactor = 1.0 - maxColorFactor

		# Calculate the RGB values of selRGB
		selectedColRed = int (siennaBrownRGB[0]*minColorFactor + 
								burlyWoodRGB[0]*maxColorFactor)
		selectedColGreen = int (siennaBrownRGB[1]*minColorFactor + 
								burlyWoodRGB[1]*maxColorFactor)
		selectedColBlue = int (siennaBrownRGB[2]*minColorFactor +
								burlyWoodRGB[2]*maxColorFactor)

		return  (selectedColRed, selectedColGreen, selectedColBlue)


	def mapColorDirtSnowGradient(self, vertHeight):
		# Calculate color by weighted average of min and maxColors
		# for this region of terrain.

		burlyWoodMinHeight = self.burlyWoodMinHeight
		snowWhiteMinHeight = self.snowWhiteMinHeight

		burlyWoodRGB = self.burlyWoodRGB
		snowWhiteRGB = self.snowWhiteRGB

		# Find gradient factors / weights of bound colors
		maxColorFactor = self.findMaxColorGradientFactor(burlyWoodMinHeight,
														 snowWhiteMinHeight,
														 vertHeight)
		minColorFactor = 1.0 - maxColorFactor

		# Calculate the RGB values of selRGB
		selectedColRed = int (burlyWoodRGB[0]*minColorFactor + 
								snowWhiteRGB[0]*maxColorFactor)
		selectedColGreen = int (burlyWoodRGB[1]*minColorFactor + 
								snowWhiteRGB[1]*maxColorFactor)
		selectedColBlue = int (burlyWoodRGB[2]*minColorFactor +
								snowWhiteRGB[2]*maxColorFactor)

		return  (selectedColRed, selectedColGreen, selectedColBlue)


	def mapColorSnowSnowGradient(self, vertHeight):
		# Calculate color by weighted average of min and maxColors
		# for this region of terrain.

		offSnowWhiteMinHeight = self.snowWhiteMinHeight
		pureWhiteSnowMinHeight = self.pureWhiteSnowMinHeight

		offSnowWhiteRGB = self.snowWhiteRGB
		pureSnowWhiteRGB = self.pureSnowWhiteRGB

		# Calculate the weights of the bound colors
		maxColorFactor= self.findMaxColorGradientFactor(offSnowWhiteMinHeight,
														pureWhiteSnowMinHeight,
														vertHeight)
		minColorFactor= 1.0- maxColorFactor

		# Calculate the RGB values of selRGB
		selectedColRed = int (offSnowWhiteRGB[0]*minColorFactor + 
								pureSnowWhiteRGB[0]*maxColorFactor)
		selectedColGreen = int (offSnowWhiteRGB[1]*minColorFactor + 
								pureSnowWhiteRGB[1]*maxColorFactor)
		selectedColBlue = int (offSnowWhiteRGB[2]*minColorFactor +
								pureSnowWhiteRGB[2]*maxColorFactor)

		return  (selectedColRed, selectedColGreen, selectedColBlue)

	def restrictRGBValue(self, colorRed, colorGreen, colorBlue):
		# RGB values must be output in range [0.0, 1.0]
		# Don't allow for outputed colors to be above 255/255.0 or below 0
		minValue = 0
		maxValue = 255/255.0
		maxCompVal = self.maxColorCompVal

		adjFloatingPointRGB = (colorRed/maxCompVal,colorGreen/maxCompVal,
														colorBlue/maxCompVal)

		(adjColorRed, adjColorGreen, adjColorBlue) = adjFloatingPointRGB
		if (adjColorRed > maxValue):
			adjColorRed = maxValue
		elif (adjColorRed < minValue):
			adjColorRed = minValue

		if (adjColorGreen > maxValue):
			adjColorGreen = maxValue
		elif (adjColorGreen < minValue):
			adjColorGreen = minValue

		if (adjColorBlue > maxValue):
			adjColorBlue = maxValue
		elif (adjColorBlue < minValue):
			adjColorBlue = minValue

		return (adjColorRed, adjColorGreen, adjColorBlue)

	def findMaxColorGradientFactor(self, minHeight, maxHeight, vertHeight):
		# Return the fraction :
		# (vertHeight - minHeight)/ (maxHeight - minHeight)
		# that calculates the fraction of proximity of vertHeight to maxHeight
		# in reference to minHeight

		return (vertHeight - minHeight)/(maxHeight - minHeight)

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

		# Maximum height value is (1.0)*255
		return (redLuminance*red + greenLuminance*green + blueLuminance*blue) 
	
	def drawValley(self):

		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )	# // Enable Vertex Arrays
		# // Enable Texture Coord Arrays
		glEnableClientState( GL_COLOR_ARRAY )	

		# Bind the Vertex Buffer Objects (VBOs) to graphics card
		# Vertex data and Color data are synced in GPU
		self.verticesVBO.bind()
		glVertexPointer(3, GL_FLOAT, 0, None)	# Inits the pointer in GPU
		self.colorCoordsVBO.bind()
		glColorPointer( 3, GL_FLOAT, 0, None)# Inits the pointer in GPU

		# DRAW THE LANDSCAPE HERE
		glDrawArrays (GL_TRIANGLES, 0, self.numVertices)
		
		# Unbind the VBOs here:
		self.colorCoordsVBO.unbind()
		self.verticesVBO.unbind()

		# // Disable Color Coord Arrays
		glDisableClientState( GL_COLOR_ARRAY )	
		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )# // Disable Vertex Arrays
		

