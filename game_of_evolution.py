#Game of Evolution
#Patrick Morgan
#2011.01.29

from random import randint, choice, shuffle, random

#initial settings
board_size = 30 #default=15
max_level = 3 #default=3
creature_names = ['vegetation', 'herbivore', 'carnivore']
phase_order = ['consume','spawn','die'] #default = consume, spawn, die
evolve_chance = .02 #This is out of 1 (ie .2 = 20%)
random_turn = False #TODO Turn this on to randomize creature turns.
print_phase = 'spawn' #Switch this to print a specic phase, 'all' prints all
competition = False #TODO True means equal levels eat each other

class gameboard():
	                
	def __init__(self):
		self.state = []
		self.new()
		self.start()
		
	def new(self):
		"""new() creates an empty gameboard with default settings."""
		self.state = []
		#print "State set:"
		while len(self.state) < board_size:
			row = ['.'] * board_size
			self.state.append(row)
		#print self.state
		
		
	def __repr__(self):	
		"""print() shows the current game board."""
		for lines in range(len(self.state)):
			for cells in self.state[lines]:
				print cells,
			print ""
		return ""

	def start(self):
		"""start() adds a starting species in the center of the board."""
		midpoint = board_size / 2 
		self.state[midpoint][midpoint] = 1


class life_cycle():

	def __init__(self, board1, board2):
		"""init() stores the gameboard and prepares the turn order."""
		self.board = board1 #sets the current gameboard
		self.old_gen = board2 #sets a board to store the previous gamestate.
		species = range(1, max_level+1) 
		species.reverse() #order is reversed, higher level creatures start.
		self.creature_order = species
		#print self.creature_order
		self.stats = {'dead':0,'spawned':0,'consumed':0,'evolved':0}
		
	def turn(self):
		"""turn() runs through a single turn of the game in order."""
		self.previous_gen()
		self.turnstats = {'dead':0, 'spawned':0, 'consumed':0, 'evolved':0}
		for phase in phase_order:
			#print phase
			exec 'self.%s()' % phase
		for event in self.turnstats:
			self.stats[event] += self.turnstats[event]

	def previous_gen(self): 
		"""previous_gen() stores an array of all the creatures from the
		previous generation so that generation can be killed off at the 
		end of the death phase."""
		for line in range(len(self.board.state)):
			for cell in range(len(self.board.state[line])):
				value = self.board.state[line][cell]
				self.old_gen.state[line][cell] = value
  
	def consume(self):
		"""consume() causes the higher level creatures to eat lower level
		creatures.  Creatures that are level 1 do not need to eat; they 
		recieve nutrients from the environment.  Creatures that are too far
		away from an appropriate food source die during this phase."""
		for species in self.creature_order:
			if species > 1:
				prey = species - 1
				creature_loc = self.grid_search(species)
				for creature in creature_loc:
					grid = self.grid_check(creature[0], creature[1])
					if prey not in grid: #starvation
						self.board.state[creature[0]][creature[1]] = '.'
						self.old_gen.state[creature[0]][creature[1]] = '.'
						self.turnstats['dead'] += 1
						#print 'Creature starved!'
					else: #consume
						#print grid
						prey_choice = []
						for i in range(len(grid)):
							if grid[i] == prey: # or grid[i] == species:
								prey_choice.append(i)
						chosen_prey = choice(prey_choice)
						#print chosen_prey
						prey_y = creature[0] + chosen_prey / 3 - 1
						prey_x = creature[1] + chosen_prey % 3 - 1
						#print 'y pos =', prey_y, ', x pos =', prey_x
						self.turnstats['consumed'] += 1
						self.board.state[prey_y][prey_x] = '.'
						self.old_gen.state[prey_y][prey_x] = '.'
		#print self.board
 
		if print_phase == 'consume' or print_phase == 'all':
			print self.board	
	    

	def spawn(self):
		"""spawn() causes creatures to generate children in	nearby open cells.
		If there is no room for their spawn, they produce no children.  Higher
		level creatures produce fewer offspring than lower levels, but they 
		reproduce first."""
		#print self.board
		#print self.creature_order, "remaining creature order"
		for species in self.creature_order:
		 	creature_loc = self.grid_search(species)
			birthrate = max_level - species + 1
			for creature in creature_loc:
				grid = self.grid_check(creature[0], creature[1])
				open_space = []
				for i in range(len(grid)):
					if grid[i] == '.':
						open_space.append(i)
				if len(open_space) <= birthrate:
					for spawn in open_space:
						spawn_y = creature[0] + spawn / 3 -1
						spawn_x = creature[1] + spawn % 3 -1
						self.board.state[spawn_y][spawn_x] = self.spawnling(species)
				else:
					shuffle(open_space)
					spawn_num = birthrate
					while spawn_num > 0:
						spawn_num -= 1
						spawn = open_space.pop()
						spawn_y = creature[0] + spawn / 3 -1
						spawn_x = creature[1] + spawn % 3 -1
						self.board.state[spawn_y][spawn_x] = self.spawnling(species)

		if print_phase == 'spawn' or print_phase == 'all':
			print self.board	
	
	def spawnling(self, species):
		self.turnstats['spawned'] += 1
		evolve = random()
		#print evolve, 'Species', species, 'evolves!'
		if evolve < evolve_chance:
			self.turnstats['evolved'] += 1
			if species == max_level:
				return species - 1
			elif species > 1:
				cointoss = random()
				if cointoss > .5:
					return species+1
				else:
					return species-1
			else: 
				return species + 1
		
		else:
			return species

	def die(self):
		"""die() kills all of the creatures from the previous turn, making way
		for the next generation of life."""
		for lines in range(len(self.old_gen.state)):
			for cells in range(len(self.old_gen.state[lines])):
				if self.old_gen.state[lines][cells] != '.':
					self.board.state[lines][cells] = '.'
					self.turnstats['dead'] += 1
        
		if print_phase == 'die' or print_phase== 'all':
			print self.board	
	    
	def grid_check(self, y, x):
		"""grid_check() takes a coordinate from the gameboard and checks its 
		surrounding cells for open spaces, other creatures, and blockades."""
		y0 = y - 1 #y0 and x0 are the starting points of the grid.
		x0 = x - 1 
		grid = []
		for row in range(3):
			for column in range(3):
				ypos = y0 + row #These set current x and y position.
				xpos = x0 + column
				if ypos == y and xpos == x: 
					grid.append('x')
				elif ypos < 0 or xpos < 0:
					grid.append('x')
				else:
					try:
   		 				grid.append(self.board.state[ypos][xpos])
	  		  		except IndexError:
		   		 		grid.append('x')
		return grid

	def grid_search(self, search):
		"""grid_search() looks for a search term and returns a list of 
		coordinates that match the search criteria."""		
		results = []
 		for row in range(len(self.board.state)):
			for column in range(len(self.board.state[row])):
				if self.board.state[row][column] == search:
					results.append((row, column))
		return results

def play():
	"""play() is the main loop for the simulation.  Pressing enter
	initiates the next life cycle.  Turns are counted and printed
	at the end of each cycle."""
	game = gameboard()
	previous = gameboard()
	evolution = life_cycle(game, previous)
	turns = 0
	print evolution.board
	while True:
		next_turn = raw_input('Press enter for next cycle:')
		turns += 1
		evolution.turn()
		#print evolution.board
		print turns
		if next_turn == 'stats':
			print evolution.stats

if __name__ == "__main__":
	play()
