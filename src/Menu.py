# Menu.py

# Creates a class in order to allow FlyPyGame instance
# to separately display the game menu in a pyglet window
# (as opposed to a GLUT window) and listen for keypress events.
# When a key is pressed, the control will return to FlyPyValley
# animation instance.

import pyglet


# Adapted from:
# <http://www.pyglet.org/doc/programming_guide/subclassing_window.html>
"""class MenuWindow(pyglet.window.Window):
	def __init__(self):

		#(winHeight, winWidth) = (400, 640)
		super(MenuWindow, self).__init__()
		#self.menuImage = pyglet.resource.image('../rsc/FlyPyValley.gif')

	# Begin the app mainloop
	def run (self):
		pyglet.app.run()

	# Draw the menu splash screen every draw call
	def on_draw(self):
		self.clear()
		self.menuImage.blit(0,0)

	def on_key_press(self, keysym, modifier):
		# Quit this pyglet application to allow for the FlyPyValley
		# game to continue
		pyglet.app.exit()

#myMenu = MenuWindow()
#pyglet.app.run()
#myMenu.run()"""
class HelloWorldWindow(pyglet.window.Window):
    def __init__(self):
        super(HelloWorldWindow, self).__init__()

        self.label = pyglet.text.Label('Hello, world!')

    def on_draw(self):
        self.clear()
        self.label.draw()

if __name__ == '__main__':
    window = HelloWorldWindow()
    pyglet.app.run()

