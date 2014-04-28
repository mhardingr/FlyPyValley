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
		self.verticesVBO = None		# Using VBOs

		self.colorCoords = None
		self.colorCoordsVBO = None # Using VBOs

		self.heightMapImage = None

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
		self.grassBladeMinHeight = 40
		self.siennaBrownMinHeight = 80
		self.burlyWoodMinHeight = 120
		self.snowWhiteMinHeight = 180
		self.pureWhiteSnowMinHeight = 255

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
		
		self.colorCoords [currIndex] = selColor
	
	def mapColorGrassGrassGradient(self, vertHeight):
		# Select color based on distance from minHeight baselines for
		# each color for "grass" section (meadow -> bladeOfGrass 
		# gradient). Use a linear eqtn to decide RGB blend
	


		meadowMinHeight = self.meadowGreenMinHeight
		grassBladeMinHeight = self.grassBladeMinHeight
	
		meadowRGB = (0,92,9)
		grassBladeRGB = (1,166,17)
		deltaRGB = (1, 74, 8)		# delta RGB per unit deltaHeight
		
		deltaHeight = grassBladeMinHeight - meadowMinHeight #(RUN) for slope

		# selRGB = meadMinHeight+ deltaRGB/deltaHeight * X
		# Here X will be difference between grassBladeMinHeight and vertHeight
		heightDiff = grassBladeMinHeight - vertHeight

		# Calculate the RGB values of selRGB
		selectedColRed = int (meadowRGB[0] + 
								deltaRGB[0]/deltaHeight * heightDiff)
		selectedColGreen = int (meadowRGB[1] + 
								deltaRGB[1]/deltaHeight * heightDiff)
		selectedColBlue = int (meadowRGB[2] +
								deltaRGB[2]/deltaHeight * heightDiff)

		print "Grass to grass!", (selectedColRed, selectedColGreen, selectedColBlue)
		return  (selectedColRed, selectedColGreen, selectedColBlue)

	def mapColorGrassDirtGradient(self, vertHeight):
		# Linearly blend RGB values of grassBladeRGB and siennaBrownRGB
		# depending on height.

		grassBladeMinHeight = self.grassBladeMinHeight
		siennaBrownMinHeight = self.siennaBrownMinHeight

		grassBladeRGB = (1, 166,17)
		siennaBrownRGB = (142, 107, 35)
		deltaRGB = ( 141, -59, 18)			# delta RGB per deltaHeight unit
		
		deltaHeight = siennaBrownMinHeight - grassBladeMinHeight

		# selRGB = grassBladeRGB+ deltaRGB/deltaHeight * X
		#Here X will be difference between siennaBrownMinHeight and vertHeight
		heightDiff = grassBladeMinHeight - vertHeight

		# Calculate the RGB values of selRGB
		selectedColRed = int (grassBladeRGB[0] + 
								deltaRGB[0]/deltaHeight * heightDiff)
		selectedColGreen = int (grassBladeRGB[1] + 
								deltaRGB[1]/deltaHeight * heightDiff)
		selectedColBlue = int (grassBladeRGB[2] +
								deltaRGB[2]/deltaHeight * heightDiff)

		print "Grass to dirt!", (selectedColRed, selectedColGreen, selectedColBlue)
		return  (selectedColRed, selectedColGreen, selectedColBlue)

	def mapColorDirtDirtGradient(self, vertHeight):
		# Linearly blend RGB values of siennaBrownRGB and burlyWoodRGB
		# depending on height.

		siennaBrownMinHeight = self.siennaBrownMinHeight
		burlyWoodMinHeight = self.burlyWoodMinHeight


		siennaBrownRGB = (142, 107, 35)
		burlyWoodRGB = (255, 211, 155)
		deltaRGB = ( 103, 104, 120)			# delta RGB per deltaHeight unit
		
		deltaHeight = burlyWoodMinHeight- siennaBrownMinHeight 

		# selRGB = siennaBrownRGB+ deltaRGB/deltaHeight * X
		#Here X will be difference between burlyWoodMinHeight and vertHeight
		heightDiff = burlyWoodMinHeight - vertHeight

		# Calculate the RGB values of selRGB
		selectedColRed = int (siennaBrownRGB[0] + 
								deltaRGB[0]/deltaHeight * heightDiff)
		selectedColGreen = int (siennaBrownRGB[1] + 
								deltaRGB[1]/deltaHeight * heightDiff)
		selectedColBlue = int (siennaBrownRGB[2] +
								deltaRGB[2]/deltaHeight * heightDiff)

		print "dirt to dirt!", (selectedColRed, selectedColGreen, selectedColBlue)
		return  (selectedColRed, selectedColGreen, selectedColBlue)

	def mapColorDirtSnowGradient(self, vertHeight):
		# Linearly blend RGB values of burlyWoodRGB and snowWhiteRGB
		# depending on height.

		burlyWoodMinHeight = self.burlyWoodMinHeight
		snowWhiteMinHeight = self.snowWhiteMinHeight

		burlyWoodRGB = (255, 211, 155)
		snowWhiteRGB = (245, 245, 245)
		deltaRGB = ( -10, 34, 90)			# delta RGB per deltaHeight unit
		
		deltaHeight = snowWhiteMinHeight - burlyWoodMinHeight

		# selRGB = burlyWoodRGB+ deltaRGB/deltaHeight * X
		#Here X will be difference between snowWhiteMinHeight and vertHeight
		heightDiff = snowWhiteMinHeight - vertHeight

		# Calculate the RGB values of selRGB
		selectedColRed = int (burlyWoodRGB[0] + 
								deltaRGB[0]/deltaHeight * heightDiff)
		selectedColGreen = int (burlyWoodRGB[1] + 
								deltaRGB[1]/deltaHeight * heightDiff)
		selectedColBlue = int (burlyWoodRGB[2] +
								deltaRGB[2]/deltaHeight * heightDiff)

		print "dirt to snow!", (selectedColRed, selectedColGreen, selectedColBlue)
		return  (selectedColRed, selectedColGreen, selectedColBlue)

	def mapColorSnowSnowGradient(self, vertHeight):
		# Linearly blend RGB values of burlyWoodRGB and snowWhiteRGB
		# depending on height.

		offSnowWhiteMinHeight = self.snowWhiteMinHeight
		pureWhiteSnowMinHeight = self.pureWhiteSnowMinHeight

		offSnowWhiteRGB = (245, 245, 245)
		pureSnowWhiteRGB = (255, 255, 255)
		deltaRGB = ( 10, 10, 10)			# delta RGB per deltaHeight unit
		
		deltaHeight = pureWhiteSnowMinHeight - offSnowWhiteMinHeight

		# selRGB = offSnowWhiteRGB+ deltaRGB/deltaHeight * X
		#Here X will be difference between pureSnowWhiteMinHeight 
		# and vertHeight
		heightDiff = snowWhiteMinHeight - vertHeight

		# Calculate the RGB values of selRGB
		selectedColRed = int (offSnowWhiteRGB[0] + 
								deltaRGB[0]/deltaHeight * heightDiff)
		selectedColGreen = int (offSnowWhiteRGB[1] + 
								deltaRGB[1]/deltaHeight * heightDiff)
		selectedColBlue = int (offSnowWhiteRGB[2] +
								deltaRGB[2]/deltaHeight * heightDiff)
		
		print "snow to snow!", (selectedColRed, selectedColGreen, selectedColBlue)
		return  (selectedColRed, selectedColGreen, selectedColBlue)

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
		

