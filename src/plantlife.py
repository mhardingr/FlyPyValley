# plantlife.py
# This will hold the class definitions of Plant entities 
# for the game.

# Objectives:
# 1) Plants will be randomly generated and randomly placed thoughout
# 2) Plants will be animatable (i.e. movable by wind)
# 3) Plants will be dynamically re-texturable to allow for :
#		i. Wetness (gloss and shine)
#		ii. Snow (shading effects and brightness)
#	 with each texture in HD (including reflective properties)
# 4) Plants are dynamically destroyable (minecraft style?)

from MoveableEntity import *

class Plantlife(MoveableEntity):
	population = 0
	def __init__(self):
		# Randomly generate coordinates
		self.data = Struct()
		self.data.xCoord = 0
		self.data.yCoord = 0
		self.data.zCoord = 0

		# Set to default texture
		self.data.texture = ""

		PlantLife.population += 1

	def getCoords(self):
		return list(self.xCoord, self.yCoord, self.zCoord)

	def getTexture(self):
		return self.texture

	def setCoords(self, coordsList):
		# reset World coordinates of PlantLife
		return 42

	def setTexture(self, texture):
		# reset texture of PlantLife
		return 42
	def weatherEventHandler(self, weatherEvent):
		return 42

class Grass(Plantlife):
	population = 0
	def __init__(self):
		self.data = Struct()
		# Set random world coordinates
		self.data.xCoord = 0
		self.data.yCoord = 0
		self.data.zCoord = 0
		# Set grass texture
		self.data.texture = ""
		Grass.population += 1

	def grassWeatherEventHandler(self, weatherEvent):
		return 42

		
