# MenuWindow.py

# Creates a class in order to allow FlyPyGame instance
# to separately display the game menu in a Tkinter window
# (as opposed to a GLUT window) and listen for keypress events.
# When a key is pressed, the control will return to FlyPyValley
# animation instance.

from Tkinter import *
import Image


# http://effbot.org/tkinterbook/canvas.htm was consulted on how to draw image
# in a Tkinter Canvas window.

class MenuWindow():
	def __init__(self):

		root= Tk()
		(winWidth, winHeight) = (640, 400)
		self.canvas = Canvas(root, width=winWidth, height=winHeight)
		splashImPath = "../rsc/FlyPyValleySplash.gif"
		# PhotoImage is a class within Tkinter recommended for these purposes
		self.menuImage = PhotoImage(file=splashImPath)	

		self.canvas.pack()	
		# Draw the menu splash image permanently (no need for redrawllAll)
		imCoords = (winWidth/2, winHeight/2)
		self.canvas.create_image(imCoords, image=self.menuImage)

		# Bind key events to root mainloop to be able to exit this menu!
		root.bind("<Key>", lambda event: self.keyPressed(event))

		self.root = root
		self.startMainloop()

	# Begin the root mainloop
	def startMainloop(self):
		self.root.mainloop()


	def keyPressed(self, event):
		# Quit this pyglet application to allow for the FlyPyValley
		# game to continue
		self.root.quit()

myMenu = MenuWindow()

