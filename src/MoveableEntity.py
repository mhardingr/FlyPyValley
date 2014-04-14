# MoveableEntity.py
# This is the highest parent class for all MoveableEntities
# in the world.

# Includes the defintion of the data struct that holds the
# data for each instance of sub-Classes
from Struct import *

class MoveableEntity:

	population = 0
	def __init__(self):
		self.data = Struct()	
		MoveableEntity.population += 1
