# WeatherEvent.py
# This Class describes how wind, snow, or rain will be handled in the world

# Objectives:
# 1) Events are of three possible types: Rain, Snow, or Wind
# 2) Events contain the vector of direction of weather event
# 3) Events contain the relative strength of the weather event
# 4) Events can OCCUR SIMULTANEOUSLY

from Struct import *

class WeatherEvent:

	def __init__(self, weatherType, dirX, dirY, dirZ, strength):
		self.data = Struct() # Initialize holder for weatherEvent data

		self.data.weatherType = weatherType	
		self.data.dirVec = (dirX,dirY,dirZ)
		self.data.strength = strength

	def getWeatherType(self):
		return self.data.weatherType

	def getWeatherVector(self):
		return self.data.dirVec

	def getWeatherStrength(self):
		return self.data.strength
		
