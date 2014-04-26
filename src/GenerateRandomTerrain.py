# GenerateRandomTerrain.py

import random
import Image
def randomHeightMapVals (heightmap, imageWidth, 
									topLeft, topRight, botLeft, 
									skewed = False, level=0):
	(maxLevel, maxHeight) = (9, 255.0)
	heightScale = maxHeight / (level+1)
	#print "\t"*level + "skewed:", skewed
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
		# Will draw these heights to the heightmap, but won't overwrite
		# previously saved pixel values
		drawHeightsToImage(heightmap, topLeft, topRight, botLeft, tLHeight,
							tRHeight, bLHeight)

		if (skewed == True):
			# IF working on a skewed (topLeft's ycoord <topRight's though
			# for normal triangles they should be the same y-coord) triangle,
			# do not recurse further from these corners
			return
		else:
			# recurse!
			recurseOnFirstQuadrant(heightmap,imageWidth,  
									topLeft, topRight, botLeft,level)
			recurseOnSecondQuadrant(heightmap,imageWidth, 
									topLeft, topRight, botLeft,level)
			recurseOnThirdQuadrant(heightmap,imageWidth,
									topLeft, topRight, botLeft,level)
			recurseOnFourthQuadrant(heightmap,imageWidth, 
									topLeft, topRight, botLeft,level)

			# Then make single call to operate on a skewedTriangle 
			#(diagonals between midpoints instead of straight 
			# horizontal lines between points) in heightmap
			isSkewed = True 
			skewedTriPts=findSkewedMidpts(imageWidth,topLeft,topRight,botLeft)
			randomHeightMapVals(heightmap, imageWidth, 
									 *skewedTriPts, 
									 skewed=isSkewed, level=level+1)

			"""isSkewed = True
			notSkewed = False
			skewedTriPts=findSkewedMidpts(imageWidth,topLeft,topRight,botLeft)
			normalTriPts=findRegularMidpts(imageWidth,topLeft,topRight,botLeft)
			
			return (randomHeightMapVals(heightmap, imageWidth,
									 *skewedTriPts, 
									 skewed=isSkewed, level=level+1)
					or randomHeightMapVals(heightmap, imageWidth, 
								*normalTriPts,
								skewed=notSkewed, level=level+1))"""

def recurseOnSecondQuadrant(heightmap,imageWidth, topLeft,topRight, 
									botLeft, currLevel):
	(botLeftX, botLeftY) = botLeft
	(topRightX, topRightY) = topRight
	(topLeftX, topLeftY) = topLeft

	# Since in the first quadrant, need to flip direction of iterating through
	# pixels, so now centerPt will be our "topLeft" in recursive design
	
	# centerPt point is midpoint between botLeft and topRight
	centerX = (botLeftX + topRightX) / 2
	centerY = (botLeftY + topRightY) / 2
	centerPt = (centerX, centerY)

	# topMiddle is point between topLeft and topRight (will act as botLeft
	# in recurisve call)
	topMiddleX = (topLeftX + topRightX) / 2
	topMiddleY = (topLeftY + topRightY) / 2
	topMiddlePt = (topMiddleX, topMiddleY)

	# leftMiddle is point between topLeft and botLeft (will act as topRight
	# in recursive call)
	leftMiddleX = (topLeftX + botLeftX) / 2
	leftMiddleY = (topLeftY + botLeftY) / 2
	leftMiddlePt = (leftMiddleX, leftMiddleY)

	# Make the recursive call to randomHeightMapVals - this is only a wrapper
	randomHeightMapVals(heightmap, imageWidth, centerPt,
						topMiddlePt, leftMiddlePt, level = currLevel + 1)

def recurseOnFirstQuadrant(heightmap, imageWidth, 
							topLeft, topRight,botLeft, currLevel):
	(botLeftX, botLeftY) = botLeft
	(topLeftX, topLeftY) = topLeft
	(topRightX, topRightY) = topRight

	# In first quadrant, do things similarly to the 4th quardrant:
	# "topLeft" in recursive call will be the midpoint between botLeft
	# and topRight (our botRightX):
	centerX = (botLeftX + topRightX) / 2
	centerY = (botLeftY + topRightY) / 2
	centerPt = (centerX, centerY)

	# "topRight" will be rightMiddlePt (midpt. between topRight and botRight)
	(botRightX, botRightY) = (topRightX, botLeftY)

	rightMiddleX = (topRightX + botRightX) / 2
	rightMiddleY = (topRightY + botRightY) / 2
	rightMiddlePt = (rightMiddleX, rightMiddleY)

	# "botLeft" will be topMiddlePt (midpt. betw. topLeft and topRight)
	topMiddleX = (topLeftX + topRightX) / 2
	topMiddleY = (topLeftY + topRightY) / 2
	topMiddlePt = (topMiddleX, topMiddleY)

	# Make recursive call to randomHeightMap vals as this is only a wrapper
	randomHeightMapVals(heightmap, imageWidth, centerPt, 
						rightMiddlePt, topMiddlePt, level=currLevel+1)

def recurseOnThirdQuadrant(heightmap, imageWidth, 
							topLeft, topRight,botLeft, currLevel):
	# Working on third quadrant inside original larger square
	(botLeftX, botLeftY) = botLeft
	(topLeftX, topLeftY) = topLeft
	(topRightX, topRightY) = topRight
	(botRightX, botRightY) = (topRightX, botLeftY)

	# "TopLeft" point in recursive call will be centerPt (midpt. b/w 
	# botLeft and topRight)
	centerX = (botLeftX + topRightX) / 2
	centerY = (botLeftY + topRightY) / 2
	centerPt = (centerX, centerY)

	# "topRight" point in rec. call wil be leftMid (midpt. b/w
	# topLeft and botLeft)
	leftMiddleX = (topLeftX + botLeftX) / 2
	leftMiddleY = (topLeftY + botLeftY) / 2
	leftMiddlePt = (leftMiddleX, leftMiddleY)

	# "botLeft" point in rec. call wil be botMiddlePt (midpt. b/w
	# botLeft and botRight)
	botMiddleX = (botLeftX + botRightX) / 2
	botMiddleY = (botLeftY + botRightY) / 2
	botMiddlePt = (botMiddleX, botMiddleY)

	# Here make recursive call to randomHeightMapVals with these values
	# in this order:
	randomHeightMapVals(heightmap, imageWidth, centerPt, 
						leftMiddlePt, botMiddlePt, level = currLevel + 1)

def recurseOnFourthQuadrant(heightmap, imageWidth, topLeft, topRight, 
								botLeft, currLevel):

	# Now begining recursion on fourth quadrant in original larger square
	(topLeftX, topLeftY) = topLeft
	(topRightX, topRightY) = topRight
	(botLeftX, botLeftY) = botLeft
	(botRightX, botRightY) = (topRightX, botLeftY)

	# "topLeft" in recursive call wil be centerPt (midpt. b/w
	# botLeft and topRight)
	centerX = (botLeftX + topRightX) / 2
	centerY = (botLeftY + topRightY) / 2
	centerPt = (centerX, centerY)

	# "topRight" in rec. call will be rightMiddlePt (midpt. b/w
	# topRight and botRight)
	rightMiddleX = (topRightX + botRightX) / 2
	rightMiddleY = (topRightY + botRightY) / 2
	rightMiddlePt = (rightMiddleX, rightMiddleY)

	# "topLeft" in rec. call will be botMiddlePt (midpt. b/w
	# botLeft and botRight)
	botMiddleX = (botLeftX + botRightX) / 2
	botMiddleY = (botLeftY + botRightY) / 2
	botMiddlePt = (botMiddleX, botMiddleY)
	# Make recursive call for fourth quadrant from here
	randomHeightMapVals(heightmap, imageWidth, centerPt,
						rightMiddlePt, botMiddlePt, level= currLevel+1)





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
randomHeightMapVals (heightmap, heightmapWidth, 
						initTLCoords, initTRCoords, initBLCoords)

# Save the image for debugging:
heightmap.save("randomHeightMap2.bmp")
print "Saved image..."