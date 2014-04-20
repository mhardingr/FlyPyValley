# TerrainMesh.py


class CMesh:
	""" // Mesh Data """
	MESH_RESOLUTION = 4.0
	MESH_HEIGHTSCALE = 1.0

	def __init__ (self):
		self.m_nVertexCount = 0;								# // Vertex Count

		self.m_pVertices = None # Numeric.array ( (), 'f') 		# // Vertex Data array
		self.m_pVertices_as_string = None						# raw memory string for VertexPointer ()

		self.m_pTexCoords = None # Numeric.array ( (), 'f') 	# // Texture Coordinates array
		self.m_pTexCoords_as_string = None						# raw memory string for TexPointer ()

		self.m_nTextureId = None;								# // Texture ID

		# // Vertex Buffer Object Names
		self.m_nVBOVertices = None;								# // Vertex VBO Name
		self.m_nVBOTexCoords = None;							# // Texture Coordinate VBO Name

		# // Temporary Data
		self.m_pTextureImage = None;							# // Heightmap Data


	def LoadHeightmap( self, szPath, flHeightScale, flResolution ):
		""" // Heightmap Loader """

		# // Error-Checking
		# // Load Texture Data
		try:
			self.m_pTextureImage = Image.open (szPath)						 	# // Open The Image
		except:
			return False

		# // Generate Vertex Field
		sizeX = self.m_pTextureImage.size [0]
		sizeY = self.m_pTextureImage.size [1]
		self.m_nVertexCount = int ( sizeX * sizeY * 6 / ( flResolution * flResolution ) );
		# self.m_pVertices = Numeric.zeros ((self.m_nVertexCount * 3), 'f') 			# // Vertex Data
		# Non strings approach
		self.m_pVertices = numpy.zeros ((self.m_nVertexCount, 3), 'f') 			# // Vertex Data
		self.m_pTexCoords = numpy.zeros ((self.m_nVertexCount, 2), 'f') 			# // Texture Coordinates

		nZ = 0
		nIndex = 0
		nTIndex = 0
		half_sizeX = float (sizeX) / 2.0
		half_sizeY = float (sizeY) / 2.0
		flResolution_int = int (flResolution)
		while (nZ < sizeY):
			nX = 0
			while (nX < sizeY):
				for nTri in xrange (6):
					# // Using This Quick Hack, Figure The X,Z Position Of The Point
					flX = float (nX)
					if (nTri == 1) or (nTri == 2) or (nTri == 5):
						flX += flResolution
					flZ = float (nZ)
					if (nTri == 2) or (nTri == 4) or (nTri == 5):
						flZ += flResolution
					x = flX - half_sizeX
					y = self.PtHeight (int (flX), int (flZ)) * flHeightScale
					z = flZ - half_sizeY
					self.m_pVertices [nIndex, 0] = x
					self.m_pVertices [nIndex, 1] = y
					self.m_pVertices [nIndex, 2] = z
					self.m_pTexCoords [nTIndex, 0] = flX / sizeX
					self.m_pTexCoords [nTIndex, 1] =  flZ / sizeY
					nIndex += 1
					nTIndex += 1

				nX += flResolution_int
			nZ += flResolution_int

		self.m_pVertices_as_string = self.m_pVertices.tostring () 
		self.m_pTexCoords_as_string = self.m_pTexCoords.tostring () 

		# // Load The Texture Into OpenGL
		self.m_nTextureID = glGenTextures (1)						# // Get An Open ID
		glBindTexture( GL_TEXTURE_2D, self.m_nTextureID );			# // Bind The Texture
		glTexImage2D( GL_TEXTURE_2D, 0, 3, sizeX, sizeY, 0, GL_RGB, GL_UNSIGNED_BYTE, 
			self.m_pTextureImage.tostring ("raw", "RGB", 0, -1))
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);

		# // Free The Texture Data
		self.m_pTextureImage = None
		return True;

	def PtHeight (self, nX, nY):
		""" // Calculate The Position In The Texture, Careful Not To Overflow """
		sizeX = self.m_pTextureImage.size [0]
		sizeY = self.m_pTextureImage.size [1]
		if (nX >= sizeX or nY >= sizeY):
			return 0

		# Get The Red, Green, and Blue Components 
		# NOTE, Python Image library starts 0 at the top of the image - so to match the windows
		# code we reverse the Y order 
		pixel = self.m_pTextureImage.getpixel ((nX, sizeY - nY - 1))
		flR = float (pixel [0])
		flG = float (pixel [1])
		flB = float (pixel [2])
		pixel = self.m_pTextureImage.getpixel ((nY, nX))

		# // Calculate The Height Using The Luminance Algorithm
		print ( (0.299 * flR) + (0.587 * flG) + (0.114 * flB) )
		return 	( (0.299 * flR) + (0.587 * flG) + (0.114 * flB) )		
