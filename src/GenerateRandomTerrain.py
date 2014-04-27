# GenerateRandomTerrain.py

import random
import Image

class RandomTerrainGenerator(object):
	def __init__(self, numPixelsPerSide, heightmapImage):

		self.pixelHeightsDict = dict()
		self.heightmap = heightmapImage

		# Fill pixelHeightsDict with empty sets to hold heights values
		for xCoord in xrange (numPixelsPerSide):
			for yCoord in xrange(numPixelsPerSide):
				self.pixelHeightsDict[(xCoord,yCoord)] = set()

	def diamondSquareMapVals(self, botLeft, botRight, topRight, topLeft,
								level = 0):
		(maximumLevel, maximumHeight,factor) = (10,255.0, 100.0)
		heightScale = maximumHeight - factor*(level+1)

		if (level >= maximumLevel):
			return
		else:

			self.setHeightsOfFourCorners(botLeft,botRight,topRight,topLeft,
											heightScale)

			self.setHeightsInDiamond(botLeft,botRight,topRight,topLeft)

			self.drawSquarePixels(botLeft,botRight,topRight,topLeft)
			self.drawCenterPixel(botLeft,botRight,topRight,topLeft)
			#self.drawDiamondPixels(botLeft,botRight,topRight,topLeft)

			# Now recurse on the four subsquares that make up larger square
			self.recurseOnUpperLeftSquare(botLeft,botRight,topRight,topLeft,
										  level)
			self.recurseOnUpperRightSquare(botLeft,botRight,topRight,topLeft,
										  level)
			self.recurseOnLowerRightSquare(botLeft,botRight,topRight,topLeft,
										  level)
			self.recurseOnLowerLeftSquare(botLeft,botRight,topRight,topLeft,
										  level)

	def drawSquarePixels(self, bLeft,bRight,tRight,tLeft):
		# Every shade of grey has RGB values of form ( X,X,X )
		# where Red = Green = Blue components

		# Since heights are mapped to range [0, 255], can set X = height 
		# for simplicity

		numColorValues = 3
		maxHeightValue = 0

		pixelHeightsDict = self.pixelHeightsDict
		# Get average heights for pixels bLeft, bRight, tRight, and tLeft
		bLHeight = sum(pixelHeightsDict[bLeft])/len(pixelHeightsDict[bLeft])
		bRHeight = sum(pixelHeightsDict[bRight])/len(pixelHeightsDict[bRight])
		tRHeight = sum(pixelHeightsDict[tRight])/len(pixelHeightsDict[tRight])
		tLHeight = sum(pixelHeightsDict[tLeft])/len(pixelHeightsDict[tLeft])

		# Restrict the color values drawn from the height values
		if (tLHeight > maxHeightValue or tLHeight < 0):
			tLHeight = maxHeightValue if tLHeight > maxHeightValue else 0
		if (bRHeight > maxHeightValue or bRHeight < 0):
			bRHeight = maxHeightValue if bRHeight > maxHeightValue else 0
		if (bLHeight > maxHeightValue or bLHeight < 0):
			blHeight = maxHeightValue if bLHeight > maxHeightValue else 0
			#################################3

		botLeftColorComp = maxHeightValue+int(bLHeight)
		botRightColorComp = maxHeightValue + int (bRHeight) 
		topLeftColorComp= maxHeightValue + int (tLHeight) 
		topRightColorComp=maxHeightValue+int(tRHeight)

		# Construct the RGB values for each point
		botLeftPtRGB = (botLeftColorComp,) * numColorValues
		botRightPtRGB = (botRightColorComp, )*numColorValues
		topLeftPtRGB = (topLeftColorComp,) * numColorValues
		topRightPtRGB = (topRightColorComp,)*numColorValues

		# Output the pixel to the heightmap image
		self.heightmap.putpixel( bLeft, botLeftPtRGB)
		self.heightmap.putpixel( tLeft, topLeftPtRGB)
		self.heightmap.putpixel( bRight, botRightPtRGB)
		self.heightmap.putpixel( tRight, topRightPtRGB)

	def drawCenterPixel(self, botLeft,botRight,topRight,topLeft):
		# Will essentially use height value of centerCoord in pixelHeightDict
		# and store 3 copies its adjusted value to RGB tuple
		numColorValues = 3
		maxHeightValue = 0
		pixelHeightsDict = self.pixelHeightsDict
		(bLX, bLY) = botLeft
		(bRX, bRY) = botRight
		(tRX, tRY) = topRight
		(tLX, tLY) = topLeft
		# Center is midpt of botLeft and topRight
		ctrPt = ((bLX+tRX) / 2, (bLY + tRY)/2)
		ctrHeight = sum(pixelHeightsDict[ctrPt])/len(pixelHeightsDict[ctrPt])

		# restrict the height value
		if (ctrHeight > maxHeightValue or ctrHeight < 0):
			ctrHeight = maxHeightValue if ctrHeight > maxHeightValue else 0

		# Construct the RGB values for each point
		ctrColorComp = maxHeightValue + int(ctrHeight)
		ctrPtRGB = (ctrColorComp,) * numColorValues

		# Output the pixel to the heightmap image
		self.heightmap.putpixel( ctrPt, ctrPtRGB)

	#def drawDiaomnd

	def recurseOnUpperLeftSquare(self, botLeft,botRight,topRight,topLeft,
									 currLevel):
		(bLX, bLY) = botLeft
		(bRX, bRY) = botRight
		(tRX, tRY) = topRight
		(tLX, tLY) = topLeft

		# NewBotLeft will be midpoint of botLeft and topLeft
		newBotLeft = ((bLX + tLX) / 2, (bLY + tLY) / 2)

		# NewBotRight will be midpoint between botLeft and topRight
		newBotRight = ((bLX + tRX) / 2, (bLY + tRY) / 2)

		# NewTopRight will be midpoint between topLeft and topRight
		newTopRight = ((tLX + tRX) / 2,(tLY + tRY) / 2)

		# newTopLeft will be old topLeft
		newTopLeft = topLeft

		self.diamondSquareMapVals(newBotLeft, newBotRight, newTopRight,
									newTopLeft,currLevel+1)

	def recurseOnUpperRightSquare(self, botLeft, botRight, topRight,topLeft,
									currLevel):
		(bLX, bLY) = botLeft
		(bRX, bRY) = botRight
		(tRX, tRY) = topRight
		(tLX, tLY) = topLeft

		# NewBotLeft will be midpoint of botLeft and topRight
		newBotLeft = ((bLX + tRX) / 2, (bLY + tRY) / 2)

		# NewBotRight will be midpoint between topRight and topLeft
		newBotRight = ((tLX + tRX) / 2, (tLY + tRY) / 2)

		# NewTopRight will be old topRight
		newTopRight = topRight

		# newTopLeft will be midpoint between topLeft and topRight
		newTopLeft = ( (tLX + tRX) / 2, (tLY + tRY) / 2)

		self.diamondSquareMapVals(newBotLeft, newBotRight, newTopRight, 
								newTopLeft,currLevel+1)
	
	def recurseOnLowerLeftSquare(self, botLeft, botRight, topRight,topLeft,
									currLevel):
		(bLX, bLY) = botLeft
		(bRX, bRY) = botRight
		(tRX, tRY) = topRight
		(tLX, tLY) = topLeft

		# NewBotLeft will be old botLeft
		newBotLeft = botLeft 

		# NewBotRight will be midpoint between botLeft and botRight
		newBotRight = ( (bLX + bRX) / 2, (bLY + bRY) / 2)

		# NewTopRight will be midpoint between botLeft and topRight
		newTopRight = ( (bLX+ tRX) / 2, (bLY + tRY) / 2)

		# newTopLeft will be midpoint between topLeft and botLeft
		newTopLeft = ( (tLX + bLX) / 2, (tLY + bLY) / 2)

		self.diamondSquareMapVals(newBotLeft, newBotRight, newTopRight,
								newTopLeft,currLevel+1)

	def recurseOnLowerRightSquare(self, botLeft, botRight, topRight,topLeft,
									currLevel):
		(bLX, bLY) = botLeft
		(bRX, bRY) = botRight
		(tRX, tRY) = topRight
		(tLX, tLY) = topLeft

		# NewBotLeft will be midpoint of botLeft and botRight
		newBotLeft = ((bLX + bRX) / 2, (bLY + bRY) / 2)

		# NewBotRight will be old botRight
		newBotRight = botRight

		# NewTopRight will be midpoint between topRight and botRight 
		newTopRight = ( (bRX + tRX) / 2, (bRY + tRY) / 2)

		# newTopLeft will be midpoint between botLeft and topRight
		newTopLeft = ( (bLX + tRX) / 2, (bLY + tRY) / 2)

		self.diamondSquareMapVals(newBotLeft, newBotRight, newTopRight,
								newTopLeft, currLevel+1)

	def setHeightsOfFourCorners(self, bLeft,bRight,tRight,tLeft,heightScale):
		# Calculate heights for 4 corners of box:
		bLHeight = random.random()*heightScale
		bRHeight = random.random()*heightScale
		tRHeight = random.random()*heightScale
		tLHeight = random.random()*heightScale		

		self.pixelHeightsDict[bLeft].add(bLHeight)
		self.pixelHeightsDict[bRight].add(bRHeight)
		self.pixelHeightsDict[tRight].add(tRHeight)
		self.pixelHeightsDict[tLeft].add(tLHeight)

	def setHeightsInDiamond(self,bLeft, bRight, tRight, tLeft): 
		(bLX, bLY) = bLeft
		(bRX, bRY) = bRight
		(tRX, tRY) = tRight
		(tLX, tLY) = tLeft

		pixelHeightsDict = self.pixelHeightsDict
		# Get average heights for pixels bLeft, bRight, tRight, and tLeft
		bLHeight = sum(pixelHeightsDict[bLeft])/len(pixelHeightsDict[bLeft])
		bRHeight = sum(pixelHeightsDict[bRight])/len(pixelHeightsDict[bRight])
		tRHeight = sum(pixelHeightsDict[tRight])/len(pixelHeightsDict[tRight])
		tLHeight = sum(pixelHeightsDict[tLeft])/len(pixelHeightsDict[tLeft])

		# set height of the center of this square to be average of corners
		ctrAvgHeight = (bLHeight + bRHeight + tRHeight + tLHeight) / 4.0
		ctrPt = (((bLX + tRX) / 2), ((bLY + tRY) / 2))
		self.pixelHeightsDict[ctrPt].add(ctrAvgHeight)


		self.setHeightsForCornersOfDiamond(bLeft, bRight, tRight, tLeft, 
										bLHeight, bRHeight,tRHeight,tLHeight)



	def setHeightsForCornersOfDiamond(self, bLeft,bRight,tRight, tLeft,
										bLHeight, bRHeight,tRHeight,tLHeight):
		(bLX, bLY) = bLeft
		(bRX, bRY) = bRight
		(tRX, tRY) = tRight
		(tLX, tLY) = tLeft

		# set Height of midpts of sides of square to average of 2 adj. corners
		midLeftAvgHeight = (bLHeight + tLHeight) / 2.0	# midpt(bLeft + tLeft)
		midTopAvgHeight = (tLHeight + tRHeight) / 2.0  #midpt(tLeft+tRight)
		midRightAvgHeight = (tRHeight + bRHeight) / 2.0 #midpt(tRight+bRight)
		midBotAvgHeight = (bLHeight + bRHeight) / 2.0  #midpt(bLeft+bRight)

		# corresponding coordinates
		midLeftCoords = ( ((bLX + tLX) / 2), ((bLY + tLY) / 2) )
		midTopCoords = ( (( tLX + tRX) / 2), ((tLY + tRY) / 2) )
		midRightCoords = ( (( tRX + bRX) / 2), ((tRY + bRY) / 2) )
		midBotCoords = ( (( bLX + bRX) / 2), ((bLY + bRY) / 2) )

		# Save these coords to self struct
		self.pixelHeightsDict[midLeftCoords].add(midLeftAvgHeight)
		self.pixelHeightsDict[midTopCoords].add(midTopAvgHeight)
		self.pixelHeightsDict[midRightCoords].add(midRightAvgHeight)
		self.pixelHeightsDict[midBotCoords].add(midBotAvgHeight)


	def randomHeightMapVals (self,botLeft, botRight, topRight, 
								topLeft,level=0):
		(maxLevel, maxHeight) = (9, 255.0)
		heightScale = maxHeight - 100*(level+1)
		
		if (level >= maxLevel):
			# Base case: don't do anything when have reached maximumLevel
			return
		else:
			# Calculate heights for topRight and botLeft points
			tLHeight = random.random()*heightScale
			bRHeight = random.random()*heightScale

			# Want to force the topleft corner to be heighest point
			# Has random height value that is scaled and sumed with
			# the difference between the topRight and botLeft heights
			absoluteHeightDiff = abs(tLHeight - bRHeight)
			bLHeight = random.random()*heightScale + absoluteHeightDiff
			# Will draw these heights to the heightmap, but won't overwrite
			# previously saved pixel values
			#print bLHeight
			drawHeightsToImage(heightmap, botLeft, topLeft, botRight, bLHeight,
								tLHeight, bRHeight)

			if (skewed == True):
				# IF working on a skewed (topLeft's ycoord <topRight's though
				# for normal triangles they should be the same y-coord) triangle,
				# do not recurse further from these corners
				return
			else:
				# recurse!
				recurseOnFirstQuadrant(heightmap, 
										botLeft,topLeft,botRight,level)
				recurseOnSecondQuadrant(heightmap,
										botLeft,topLeft,botRight,level)
				recurseOnThirdQuadrant(heightmap,
										botLeft,topLeft,botRight,level)
				recurseOnFourthQuadrant(heightmap,
										botLeft,topLeft,botRight,level)

				# Then make single call to operate on a skewedTriangle 
				#(diagonals between midpoints instead of straight 
				# horizontal lines between points) in heightmap
				isSkewed = False 
				skewedTriPts=findSkewedMidpts(botLeft,topLeft,botRight,)
				randomHeightMapVals(heightmap,
										 *skewedTriPts, 
										 skewed=isSkewed, level=level+1)

				"""isSkewed = True
				notSkewed = False
				skewedTriPts=findSkewedMidpts(topLeft,topRight,botLeft)
				normalTriPts=findRegularMidpts(topLeft,topRight,botLeft)
				
				return (randomHeightMapVals(heightmap, 
										 *skewedTriPts, 
										 skewed=isSkewed, level=level+1)
						or randomHeightMapVals(heightmap, 
									*normalTriPts,
									skewed=notSkewed, level=level+1))"""

	def recurseOnFirstQuadrant(heightmap, 
								botLeft,topLeft,botRight, currLevel):
		(botLeftX, botLeftY) = botLeft
		(topLeftX, topLeftY) = topLeft
		(botRightX, botRightY) = botRight
		(topRightX, topRightY) = (botRightX, topLeftY)
		# In first quadrant, do things similarly to the 4th quardrant:

		# "botLeft" in recursive call will be the midpoint between botLeft
		# and topRight (our topRight):
		topRightPt = (topRightX, topRightY)
		"""centerX = (botLeftX + topRightX) / 2
		centerY = (botLeftY + topRightY) / 2
		centerPt = (centerX, centerY)"""

		# "topLeft" will be rightMiddlePt (midpt. betw. topRight and botRight)
		rightMiddleX = (topRightX + botRightX) / 2
		rightMiddleY = (topRightY + botRightY) / 2
		rightMiddlePt = (rightMiddleX, rightMiddleY)

		# "botRight" will be topMiddlePt (midpt. between topLeft and topRight)
		topMiddleX = (topLeftX + topRightX) / 2
		topMiddleY = (topLeftY + topRightY) / 2
		topMiddlePt = (topMiddleX, topMiddleY)

		# Make recursive call to randomHeightMap vals as this is only a wrapper
		randomHeightMapVals(heightmap,  topRightPt, 
							rightMiddlePt, topMiddlePt, level=currLevel+1)

	def recurseOnSecondQuadrant(heightmap, botLeft,topLeft, 
										botRight, currLevel):
		(botLeftX, botLeftY) = botLeft
		(topLeftX, topLeftY) = topLeft
		(botRightX, botRightY) = botRight
		(topRightX, topRightY) = (botRightX, topLeftY)

		# Since in the first quadrant, need to flip direction of iterating through
		# pixels, so now topLeft will be our "botLeft" in recursive design
		# "botLeft" in rec. call is topLeftPt
		topLeftPt = topLeft

		# leftMiddle is point between topLeft and botLeft (will act as botRight
		# in recursive call)
		leftMiddleX = (topLeftX + botLeftX) / 2
		leftMiddleY = (topLeftY + botLeftY) / 2
		leftMiddlePt = (leftMiddleX, leftMiddleY)

		# topMiddlePt is point between botLeft and topRight (will act as topLeft
		# in recurisve call)
		# centerPt point is midpoint between botLeft and topRight
		"""centerX = (botLeftX + topRightX) / 2
		centerY = (botLeftY + topRightY) / 2
		centerPt = (centerX, centerY)"""
		topMiddleX = (topLeftX + topRightX) / 2
		topMiddleY = (topLeftY + topRightY) / 2
		topMiddlePt = (topMiddleX, topMiddleY)



		# Make the recursive call to randomHeightMapVals - this is only a wrapper
		randomHeightMapVals(heightmap,  topLeftPt, leftMiddlePt,
							 topMiddlePt, level = currLevel + 1)

	def recurseOnThirdQuadrant(heightmap, 
								botLeft, topLeft,botRight, currLevel):
		# Working on third quadrant inside original larger square
		(botLeftX, botLeftY) = botLeft
		(topLeftX, topLeftY) = topLeft
		(botRightX, botRightY) = botRight

		# "botLeft" point in rec. call wil be botLeft
		botLeftPt = botLeft
		"""botMiddleX = (botLeftX + botRightX) / 2
		botMiddleY = (botLeftY + botRightY) / 2
		botMiddlePt = (botMiddleX, botMiddleY)"""

		# "topLeft" point in rec. call wil be leftMid (midpt. b/w
		# topLeft and botLeft)
		leftMiddleX = (topLeftX + botLeftX) / 2
		leftMiddleY = (topLeftY + botLeftY) / 2
		leftMiddlePt = (leftMiddleX, leftMiddleY)

		# "botRight" point in recursive call will be botMiddle (midpt. b/w 
		# botLeft and botRight)
		botMiddleX = (botLeftX + botRightX) / 2
		botMiddleY = (botLeftY + botRightY) / 2
		botMiddlePt = (botMiddleX, botMiddleY)

		# Here make recursive call to randomHeightMapVals with these values
		# in this order:
		randomHeightMapVals(heightmap, botLeftPt, 
							leftMiddlePt, botMiddlePt, level = currLevel + 1)

	def recurseOnFourthQuadrant(heightmap, botLeft, topLeft, 
									botRight, currLevel):

		# Now begining recursion on fourth quadrant in original larger square
		(botLeftX, botLeftY) = botLeft
		(topLeftX, topLeftY) = topLeft
		(botRightX, botRightY) = botRight
		(topRightX, topRightY) = (botRightX, topLeftY)

		# "botLeft" in rec. call will be botRight (midpt. b/w
		# botLeft and botRight)
		botRightPt = botRight

		# "topLeft" in recursive call wil be botMiddlePt (midpt. b/w
		# botLeft and topRight)
		botMiddleX = (botLeftX + botRightX) / 2
		botMiddleY = (botLeftY + botRightY) / 2
		botMiddlePt = (botMiddleX, botMiddleY)
		"""centerX = (botLeftX + topRightX) / 2
		centerY = (botLeftY + topRightY) / 2
		centerPt = (centerX, centerY)"""

		# "botRight" in rec. call will be rightMiddlePt (midpt. b/w
		# topRight and botRight)
		rightMiddleX = (topRightX + botRightX) / 2
		rightMiddleY = (topRightY + botRightY) / 2
		rightMiddlePt = (rightMiddleX, rightMiddleY)


		# Make recursive call for fourth quadrant from here
		randomHeightMapVals(heightmap, botRightPt,
							botMiddlePt, rightMiddlePt,  level= currLevel+1)


	def findSkewedMidpts(botLeftPt,topLeftPt,botRightPt):
		(topLeftX, topLeftY) = topLeftPt
		(botRightX, botRightY) = botRightPt
		(botLeftX, botLeftY) = botLeftPt
		(topRightX, topRightY) = (botRightX, topLeftY)

		# Find the midpoint of the line connecting topLeft and botLeft
		leftmostMidptX = (topLeftX + botLeftX) / 2
		leftmostMidptY = (topLeftY + botLeftY) / 2

		# Find the midpoint of the line connecting topLeft and topRight
		upperMidptX = (topLeftX + topRightX) / 2
		upperMidptY = (topLeftY + topRightY) / 2

		# Find the midpoint for the line connecting botLeft with botRight
		# botRight not given point so really is just moving botLeft 1/2 width
		# to the right
		lowerMidptX = (botLeftX + botRightX) / 2
		lowerMidptY = (botLeftY + botRightY) / 2

		# Package the coordinates into tuples
		leftmostMidpt = (leftmostMidptX, leftmostMidptY)
		upperMidpt = (upperMidptX, upperMidptY)
		lowerMidpt = (lowerMidptX, lowerMidptY)
		return ( leftmostMidpt, upperMidpt, lowerMidpt )


	def drawHeightsToImage(heightmap, botLeft, topLeft, botRight, bLHeight,
								tLHeight, bRHeight):
		# Every shade of grey has RGB values of form ( X,X,X )
		# where Red = Green = Blue components

		# Since heights are mapped to range [0, 255], can set X = height 
		# for simplicity

		numColorValues = 3
		maxHeightValue = 0

		# Restrict the color values drawn from the height values
		if (tLHeight > maxHeightValue or tLHeight < 0):
			tLHeight = maxHeightValue if tLHeight > maxHeightValue else 0
		if (bRHeight > maxHeightValue or bRHeight < 0):
			bRHeight = maxHeightValue if bRHeight > maxHeightValue else 0
		if (bLHeight > maxHeightValue or bLHeight < 0):
			blHeight = maxHeightValue if bLHeight > maxHeightValue else 0

		currBLColor =heightmap.getpixel(botLeft)[0]
		currTLColor =heightmap.getpixel(topLeft)[0]
		currBRColor = heightmap.getpixel(botRight)[0]

		botLeftColorComp = ((maxHeightValue+int(bLHeight)) + currBLColor) / 2
		topLeftColorComp= ((maxHeightValue + int (tLHeight)) + currTLColor)/2
		botRightColorComp = ((maxHeightValue + int (bRHeight)) + currBRColor)/2
		
		# Construct the RGB values for each point
		botLeftPtRGB = (botLeftColorComp,) * numColorValues
		topLeftPtRGB = (topLeftColorComp,) * numColorValues
		botRightPtRGB = (botRightColorComp, )*numColorValues

		# Output the pixel to the heightmap image
		heightmap.putpixel( botLeft, botLeftPtRGB)
		heightmap.putpixel( topLeft, topLeftPtRGB)
		heightmap.putpixel( botRight, botRightPtRGB)

print "Biatch"
heightmapSize = (256, 256)
blankSpaceColor = "white"
heightmap = Image.new("RGB", heightmapSize, blankSpaceColor)

initTLCoords = (0, 0)
initTRCoords = (0, 255)
initBLCoords = (255, 0)
initBRCoords = (255, 255)
heightmapWidth = heightmapHeight = 256
randomTerraGenerator = RandomTerrainGenerator(heightmapWidth,heightmap)
randomTerraGenerator.diamondSquareMapVals (initTLCoords, initTRCoords, 
											initBLCoords, initBRCoords)

# Save the image for debugging:
heightmap.save("../rsc/diamondSquareAlgorithmTest1.bmp")
print "Saved image..."