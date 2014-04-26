# GenerateRandomTerrain.py

import random
import Image
def randomHeightMapVals (heightmap, imageWidth, imageHeight, 
									topLeft, topRight, botLeft, 
									skewed = False, level=0):
	(maxLevel, maxHeight) = (10, 255.0)
	heightScale = maxHeight / (level+1)
	print "\t"*level + "skewed:", skewed
	if (level >= maxLevel):
		# Base case: don't do anything when have reached maximumLevel
		return
	else:
		# Calculate heights for topRight and botLeft points
		tRHeight = random.random()*heightScale
		bLHeight = random.random()*heightScale

		# Want to force the topleft corner to be heighest point
		# Has random height value that is scaled and sumed with
		# the difference between the topRight and botLeft heights
		absoluteHeightDiff = abs(tRHeight - bLHeight)
		tLHeight = random.random()*heightScale + absoluteHeightDiff
		print "\t"*level + "heights: (%5f,%5f,%5f)" % (tLHeight,tRHeight,bLHeight)
		# Will draw these heights to the heightmap, but won't overwrite
		# previously saved pixel values
		drawHeightsToImage(heightmap, topLeft, topRight, botLeft, tLHeight,
							tRHeight, bLHeight)

		if (skewed == True):
			# IF working on a skewed (topLeft's ycoord <topRight's though
			# for normal triangles they should be the same y-coord) triangle, do not recurse
			# further from these corners
			return
		else:
			# recurse!
			recurseOnFirstQuadrant(heightmap,imageWidth, imageHeight, topLeft, topRight, 
									botLeft,level)
			recurseOnSecondQuadrant(heightmap,imageWidth, imageHeight, topLeft, topRight, 
									botLeft,level)
			recurseOnThirdQuadrant(heightmap,imageWidth, imageHeight, topLeft, topRight, 
									botLeft,level)
			recurseOnFourthQuadrant(heightmap,imageWidth, imageHeight, topLeft, topRight, 
									botLeft,level)

			"""isSkewed = True
			notSkewed = False
			skewedTriPts=findSkewedMidpts(imageWidth,topLeft,topRight,botLeft)
			normalTriPts=findRegularMidpts(imageWidth,topLeft,topRight,botLeft)
			
			return (randomHeightMapVals(heightmap, imageWidth, imageHeight,
									 *skewedTriPts, 
									 skewed=isSkewed, level=level+1)
					or randomHeightMapVals(heightmap, imageWidth, imageHeight,
								*normalTriPts,
								skewed=notSkewed, level=level+1))"""

def recurseOnFirstQuadrant(heightmap,imageWidth, imageHeight, topLeft,topRight, 
									botLeft,level)


def findSkewedMidpts(imWidth, topLeftPt,topRightPt,botLeftPt):
	(topLeftX, topLeftY) = topLeftPt
	(topRightX, topRightY) = topRightPt
	(botLeftX, botLeftY) = botLeftPt

	# Find the midpoint of the line connecting topLeft and botLeft
	leftmostMidptX = (topLeftX + botLeftX) / 2
	leftmostMidptY = (topLeftY + botLeftY) / 2

	# Find the midpoint of the line connecting topLeft and topRight
	upperMidptX = (topLeftX + topRightX) / 2
	upperMidptY = (topLeftY + topRightY) / 2

	# Find the midpoint for the line connecting botLeft with botRight
	# botRight not given point so really is just moving botLeft 1/2 width
	# to the right
	lowerMidptX = (botLeftX + imWidth) / 2
	lowerMidptY = botLeftY

	# Package the coordinates into tuples
	leftmostMidpt = (leftmostMidptX, leftmostMidptY)
	upperMidpt = (upperMidptX, upperMidptY)
	lowerMidpt = (lowerMidptX, lowerMidptY)
	return ( leftmostMidpt, upperMidpt, lowerMidpt )

def findRegularMidpts(imWidth, topLeftPt, topRightPt, botLeftPt):
	(topLeftX, topLeftY) = topLeftPt
	(topRightX, topRightY) = topRightPt
	(botLeftX, botLeftY) = botLeftPt
	# Find the coords of the bottomRight point that isn't passed in
	(botRightX, botRightY) = (imWidth, botLeftY)
	
	# Find the midpoint of topLeft with botRight
	newTopLeftX = (topLeftX + botRightX) / 2
	newTopLeftY = (topLeftY + botRightY) / 2

	# Find the midpoint of topRight with botRight
	newTopRightX = (topRightX + botRightX) / 2
	newTopRightY = (topRightY + botRightY) / 2

	# Find the midpoint for botLeft with botRight
	newBotLeftX = (botLeftX + botRightX) / 2
	newBotLeftY = (botLeftY + botRightY) / 2

	# Package the coords into tuples
	newTopLeftPt = (newTopLeftX, newTopLeftY)
	newTopRightPt = (newTopRightX, newTopRightY)
	newBotLeftPt = (newBotLeftX, newBotLeftY)

	return ( newTopLeftPt, newTopRightPt, newBotLeftPt )

def drawHeightsToImage(heightmap, topLeft, topRight, botLeft, tLHeight,
							tRHeight, bLHeight):
	# Every shade of grey has RGB values of form ( X,X,X )
	# where Red = Green = Blue components

	# Since heights are mapped to range [0, 255], can set X = height 
	# for simplicity

	numColorValues = 3
	maxHeightValue = 255
	print "Drawing heights to image!"

	# Restrict the color values drawn from the height values
	if (tLHeight > maxHeightValue):
		tLHeight = maxHeightValue
	if (tRHeight > maxHeightValue):
		tRHeight = maxHeightValue
	if (bLHeight > maxHeightValue):
		blHeight = maxHeightValue

	topLeftColorComp = (maxHeightValue-int(tLHeight)) 
	topRightColorComp= (maxHeightValue - int (tRHeight))
	botLeftColorComp = (maxHeightValue - int (bLHeight))
	
	# Construct the RGB values for each point
	topLeftPtRGB = (topLeftColorComp,) * numColorValues
	topRightPtRGB = (topRightColorComp,) * numColorValues
	botLeftPtRGB = (botLeftColorComp, )*numColorValues

	# Output the pixel to the heightmap image
	heightmap.putpixel( topLeft, topLeftPtRGB)
	heightmap.putpixel( topRight, topRightPtRGB)
	heightmap.putpixel( botLeft, botLeftPtRGB)

print "Biatch"
heightmapSize = (256, 256)
blankSpaceColor = "white"
heightmap = Image.new("RGB", heightmapSize, blankSpaceColor)

initTLCoords = (0, 0)
initTRCoords = (0, 255)
initBLCoords = (255, 0)
heightmapWidth = heightmapHeight = 256
randomHeightMapVals (heightmap, heightmapWidth, heightmapHeight, 
					initTLCoords, initTRCoords, initBLCoords)

# Save the image for debugging:
heightmap.save("randomHeightMap1.bmp")
print "Saved image..."