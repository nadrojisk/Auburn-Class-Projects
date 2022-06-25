#!/usr/bin/python3

# author: Deacon Seals

# use: python3 worldCheck.py worldFilePath0 worldFilePath1 ... worldFilePathN
# use note: Bash regex filename expressions supported

'''
Basic checks performed:
*valid characters
*valid delineation
*correct number of elements per line
*valid map dimensions
*starting location of pac-man and ghosts
*collision detection
*basic bounds checking
'''

import sys

softErrors = []

class FormattingError(Exception):
	def __init__(self, errors):
		self.errors = errors

'''
desc:	Utility printing function that takes in a list of zero-indexing line numbers.
'''
def printLines(lines):
	message = ""
	if len(lines) == 1:
		message = "line "+repr(lines[0]+1)
	elif len(lines) > 1:
		message = "lines "+repr(lines[0]+1)
		for i in range(1,len(lines)):
			message += ", "+repr(lines[i]+1)
	return message

'''
desc:	Checks for any invalid characters in the document and squawks if it finds anything.

pre:	Input `text` is a list of strings.
'''
def checkCharacters(text):
	errors = []
	errata = dict()
	for line in range(len(text)):
		for char in text[line]:
			if char.casefold() not in "mpwft0123456789 ":
				if char not in errata: # we found an illegal character
					errata[char] = set()
				errata[char].add(line)

	# form error messages
	if errata:
		for char in errata:
			lines = list(errata[char])
			message = "invalid character "+repr(char)+" found on "
			
			if len(lines) > 1:
				lines.sort()
			message += printLines(lines)
			errors.append(message)

	if errors: raise FormattingError(errors)
	
	return
'''
desc:	Checks for formatting issues including: proper space delineation, correct
		number of elements per line, existance of height and width, correct per-line format.

pre:	Input `text` is a list of strings that has been ran through checkCharacters
		to catch any invalid characters.
'''
def checkStructure(text):
	errors = []
	width = 0
	height = 0
	global softErrors

	# iterate over text and ignore tailing blank lines
	# note: our initial rstrip formatting clears all space-only lines
	for line in range(len(text)):
		if text[-(line+1)]:
			if line > 0:
				text = text[:-line]
			break
	
	if text:
		# check width and height
		if text[0].isdigit() and '.' not in text[0]:
			width = int(text[0])
		else:
			errors.append("invalid width")
		if len(text) > 1:
			if text[1].isdigit() and '.' not in text[1]:
				height = int(text[1])
			else:
				errors.append("invalid height")

		blankLines = []
		noDelineation = set()
		tooManySpaces = set()
		tooFewElements = []
		tooManyElements = []
		wrongFormat = []

		# iterate over all lines in the text after the height and width declarations
		for line in range(2,len(text)):
			if text[line]:
				# check for correct number of space delineation characters
				if text[line].count(" ") == 0:
					noDelineation.add(line)
				elif text[line].count(" ") > 2:
					tooManySpaces.add(line)

				# try to split string since spaces exist
				if text[line].count(" ") > 0:
					# segment line and ignore blank elements caused by extra spaces
					segmented = [element for element in text[line].split(" ") if element]
					
					# check number of elements in segmented line
					if len(segmented) < 3: # could be too few elements or line of just spaces
						tooFewElements.append(line)
					elif len(segmented) > 3: # more elements than expected
						tooManyElements.append(line)
						tooManySpaces.discard(line) # actually had too many elements instead of too many spaces
					else:
						# check for two integer values in elements 1 and 2
						if not(segmented[1].isdigit() and '.' not in segmented[1]) or \
						not(segmented[2].isdigit() and '.' not in segmented[2]):
							wrongFormat.append(line) 
			else:
				blankLines.append(line)

		# blank lines don't actully break the visualizer, but you shouldn't have them
		if blankLines:
			softErrors.append("unexpected blank line found on "+printLines(blankLines))

		# make error messages if we found anything in this portion
		noDelineation = list(noDelineation)
		tooManySpaces = list(tooManySpaces)

		if len(noDelineation) > 1:
			noDelineation.sort()
		if len(tooManySpaces) > 1:
			tooManySpaces.sort()

		if noDelineation:
			errors.append("there is no space delineation on "+printLines(noDelineation))
		if tooManySpaces:
			errors.append("there are too many spaces on "+printLines(tooManySpaces))
		if tooFewElements:
			errors.append("there are too few elements on "+printLines(tooFewElements))
		if tooManyElements:
			errors.append("there are too many elements on "+printLines(tooManyElements))
		if wrongFormat:
			errors.append("correct format of 'indicator integer integer' was not followed on "+printLines(wrongFormat))
	else:
		errors.append("file is empty")

	if errors: raise FormattingError(errors)

	return width, height
'''
desc:	Checks for valid dimensions, capitalization, starting positions, object collision,
		invalid declarations after start of game, and out-of-bounds movement and placement.

pre:	Input `text` is a list of strings; `width` and `height` are integer values. All inputs
		have been used or generated by the checkStructure function to catch the errors considered
		in that function.
'''
def checkContent(text, height, width):
	
	# utility functions
	def getElements(line):
		return line[0], (int(line[1]), int(line[2]))

	def getStartLoc(piece, world):
		for line in world:
			if len(line) < 3:
				continue
			target, location = getElements(line)
			if target == piece:
				return location
		return (-1,-1)

	def inWidth(location, width):
		return location[0] >= 0 and location[0] < width
	def inHeight(location, height):
		return location[1] >= 0 and location[1] < height
	
	def manhattanDistance(location0, location1):
		return sum([abs(coord[0]-coord[1]) for coord in zip(list(location0),list(location1))]) # very extra
	
	errors = []
	errata = dict()
	
	critical = False
	declarations = True

	walls = set()
	pills = set()
	validPieces = {"m","1","2","3","f","t","p","w"}
	objects = validPieces - {"t"}
	moving = objects - {"f","p","w"}
	pacStart = (0, height-1)
	ghostStart = (width-1, 0)
	missing = (-1,-1)
	expectedStart = missing # probably a C++ habit
	message = "" # same ^^^
	fruit = set()
	movingLocations = {"m":[]} # support multiple pac-people
	

	# check for reasonable dimensions
	if width < 2:
		errors.append("width must be at least 2")
	if height < 2:
		errors.append("height must be at least 2")

	# separate text into non-uniform 2D list
	world = [[element for element in line.split(' ') if element] for line in text]

	# check for errors relating to character capitalization
	capitals = [line[0] for line in world[2:] if line and line[0] not in validPieces and line[0].casefold() in validPieces]
	if capitals:
		message = "detected incorrect use of capital letters for character(s) "
		for letter in capitals:
			message += " "+repr(letter)
		errors.append(message)

	if errors: raise FormattingError(errors)

	# check starting position of pac-man and ghosts (moving pieces)
	for player in moving:
		location = getStartLoc(player,world)

		if player == "m":
			message = "pac-man"
			expectedStart = pacStart
			movingLocations[player].append(location)
		else:
			message = "ghost "+player
			expectedStart = ghostStart
			movingLocations[player] = [location]
		
		if location == missing: # missing piece
			errors.append("couldn't find expected "+message+" character "+repr(player))
			critical = True
		elif location != expectedStart: # unexpected starting location
			errors.append("expected "+message+" starting location of "+repr(expectedStart)+" but got "+repr(location))

	# live to squawk another day unless players are missing
	if errors and critical:
		errors.append("PARSING INTERRUPTED due to critical error")
		raise FormattingError(errors)

	# iterate over all lines in the text after the height and width declarations
	for line in range(2,len(world)):
		
		# skip blank lines
		if not world[line]:
			continue

		piece, location = getElements(world[line])
		
		# check the first element
		if piece not in validPieces:
			errors.append("invalid first element "+repr(piece)+" on line "+repr(line+1))
		else:
			# check out of bounds placements or movements
			if piece in objects: # physical objects
				horizontal = inWidth(location, width)
				vertical = inHeight(location, height)
				if not horizontal or not vertical: # went out of bounds
					message = piece+" went out of bounds "
					if not horizontal and not vertical: # horizontally and vertically (alarming)
						message += "horizontally and vertically"
					elif not horizontal: # horizontally
						message += "horizontally"
					else: # vertically
						message += "vertically"
					message += " at location "+repr(location)+" on line "+repr(line+1)
					errors.append(message)
					errors.append("PARSING INTERRUPTED due to critical error on line "+repr(line+1))
					raise FormattingError(errors)

			if piece == "w": # walls
				if declarations and location not in walls: # new wall
					walls.add(location)
				elif not declarations and location not in walls: # late wall declaration
					errors.append("unexpected wall declaration after game start on line "+repr(line+1))
					errors.append("PARSING INTERRUPTED due to critical error on line "+repr(line+1))
					raise FormattingError(errors)
				else: # duplicate wall declaration
					errors.append("wall on line "+repr(line+1)+" is already defined")
				
				if location in pills: # you spawned on a pill
					errors.append("wall spawned onto a pill at location "+repr(location)+" on line "+repr(line+1))
				
				if location in [loc for player in movingLocations for loc in movingLocations[player]]: # you spawned on someone
					errors.append("wall spawned onto a player at location "+repr(location)+" on line "+repr(line+1))
					errors.append("PARSING INTERRUPTED due to critical error on line "+repr(line+1))
					raise FormattingError(errors)
			
			elif piece == "p": # pills
				if declarations and location not in pills: # new pill
					pills.add(location)
				elif not declarations and location not in pills: # late pill declaration
					errors.append("unexpected pill declaration after game start on line "+repr(line+1))
					errors.append("PARSING INTERRUPTED due to critical error on line "+repr(line+1))
					raise FormattingError(errors)
				else: # duplicate pill declaration
					errors.append("pill on line "+repr(line+1)+" is already defined")
				
				if location in walls: # you spawned in a wall
					errors.append("pill spawned into a wall at location "+repr(location)+" on line "+repr(line+1))
				
				if location in movingLocations["m"]: # you spawned on pac-man
					errors.append("pill spawned onto a player at location "+repr(location)+" on line "+repr(line+1))
			
			elif piece in moving: # pac-man and ghosts
				if piece == "m":
					message = "pac-man"
					fruit.discard(location)
					pills.discard(location)
					
					# partial support for multiple pac-people
					for person in range(len(movingLocations[piece])):
						distance = manhattanDistance(location,movingLocations[piece][person])
						if distance == 1 or (piece == "m" and distance == 0): # this has a bug if pac-people are one apart and only one moves (wip)
							movingLocations[piece][person] = location
							break
					else: # only executes if the for loop completes without breaking
						errors.append(message+" made an invalid move into location "+repr(location)+" on line "+repr(line+1))
						errors.append("PARSING INTERRUPTED due to critical error on line "+repr(line+1))
						raise FormattingError(errors)
				else:
					message = "ghost "+piece
					if manhattanDistance(location, movingLocations[piece][0]) == 1 or declarations: # all ghost moves should have a distance of 1
						movingLocations[piece][0] = location
					else:
						errors.append(message+" made an invalid move into location "+repr(location)+" on line "+repr(line+1))
						errors.append("PARSING INTERRUPTED due to critical error on line "+repr(line+1))
						raise FormattingError(errors)

				if location in walls: # you ran into a wall
					errors.append(message+" ran into a wall at location "+repr(location)+" on line "+repr(line+1))
					errors.append("PARSING INTERRUPTED due to critical error on line "+repr(line+1))
					raise FormattingError(errors)

			elif piece == "f": # fruit
				if location in walls: # you spawned in a wall
					errors.append("fruit spawned into a wall at location "+repr(location)+" on line "+repr(line+1))
					errors.append("PARSING INTERRUPTED due to critical error on line "+repr(line+1))
					raise FormattingError(errors)
				
				if location in pills: # you spawned on a pill
					errors.append("fruit spawned into a pill at location "+repr(location)+" on line "+repr(line+1))
				
				if location in fruit and location not in movingLocations["m"]: # duplicate fruit spawns 
					message = "duplicate fruit declarations at location "+repr(location)+" on "
					if message not in errata:
						errata[message] = []
					errata[message].append(line)
				else:
					fruit.add(location)
			elif piece == "t": # time
				if declarations:
					if list(pills & walls):
						message = "intersection between pills and walls at game location(s)"
						for loc in list(pills & walls):
							message += " "+repr(loc)
					declarations = False
					time = location[0]
					score = location[1]
					if score != 0:
						errors.append("starting score is non-zero")
				else:
					if time - location[0] == 1:
						time = location[0] # update time if correct
					else: # incorrect time counting
						errors.append("time didn't decrease by 1 as expected on line "+repr(line+1))
					
					if location[1] - score < 0: # score erroneously decreased
						errors.append("score decremented unexpectedly on line "+repr(line+1))
				score = location[1]


	for error in errata:
		errors.append(error+printLines(errata[error]))

	if errors: raise FormattingError(errors)
	return
'''
desc:	High-level function that calls an performs all checks in the desired order. Presents
		soft errors and comments if everything went well. For specific checks, see descriptions
		for the functions it calls.
'''
def checkWorld(filename):
	worldText = []
	global softErrors

	with open(filename, 'r') as file:
		worldText = [line.rstrip() for line in file]

	if worldText:
		try:
			checkCharacters(worldText)
			width, height = checkStructure(worldText)
			checkContent(worldText, height, width)

			for error in softErrors:
				print(filename+": [warning] "+error)
			if not softErrors:
				print(filename+": PASS")
			softErrors.clear()

		except FormattingError as e:
			for error in e.errors:
				print(filename+": [ERROR] "+ error)


def main():
	if len(sys.argv) < 2:
		print("Please pass in a world file")
	else:
		for arg in range(1,len(sys.argv)):
			checkWorld(sys.argv[arg])

if __name__ == '__main__':
	main()