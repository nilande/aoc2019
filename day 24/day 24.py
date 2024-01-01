#
# Classes
#
class ErisModel:
    def __init__(self, init_string: str):
        state = 0
        state_modifier = 1
        for c in init_string:
            match c:
                case '.':
                    state_modifier <<= 1
                case '#':
                    state |= state_modifier
                    state_modifier <<= 1
        self.state = state

        self.initialize_lookups()

    def initialize_lookups(self):
        tiles = set()
        self.neighbors = [0] * 25
        self.stay_alive = [[] for _ in range(25)]
        self.spawn = [set() for _ in range(25)]
        for r in range(5):
            for c in range(5):
                tiles.add(c + r*1j)
        for tile in tiles:
            id = self.get_id(tile)
            neighbors = {tile+1, tile-1, tile+1j, tile-1j} & tiles
            for n1 in neighbors:
                n1_id = 1 << self.get_id(n1)
                self.neighbors[id] |= n1_id
                self.stay_alive[id].append(n1_id)
                for n2 in neighbors:
                    n2_id = 1 << self.get_id(n2)
                    self.spawn[id].add(n1_id | n2_id)
            self.spawn[id] = list(self.spawn[id])

    def get_id(self, tile: complex) -> int:
        return int(tile.real) + 5*int(tile.imag)

    def draw(self, state = None):
        if state is None: state = self.state
        state_string = ''
        for r in range(5):
            for c in range(5):
                if state & 1: state_string += '#'
                else: state_string += '.'
                state >>= 1
            state_string += '\n'
        print(state_string)

    def evolve(self):
        state = self.state
        new_state = 0
        state_modifier = 1
        for i in range(25):
            if state & 1 << i:  # Cell is alive
                if state & self.neighbors[i] in self.stay_alive[i]:
                    new_state |= 1 << i # state_modifier
            else:               # Cell is dead
                if state & self.neighbors[i] in self.spawn[i]:
                    new_state |= 1 << i # state_modifier
            #state_modifier <<= 1
        self.state = new_state

class RecursiveErisModel:
    def __init__(self, init_string: str) -> None:
        bugs = set()
        for i, c in enumerate(init_string.replace('\n', '')):
            if c == '#': bugs.add((i%5+i//5*1j, 0))
        self.bugs = bugs

    def get_neighbors(self, tile: tuple) -> set:
        pos, dim = tile
        neighbors = {(pos+1, dim), (pos-1, dim), (pos+1j, dim), (pos-1j, dim)}
        for nb, _ in list(neighbors):
            if nb == 2+2j:
                match nb-pos:
                    case 1+0j: neighbors |= {(0+0j, dim+1), (0+1j, dim+1), (0+2j, dim+1), (0+3j, dim+1), (0+4j, dim+1)}
                    case -1+0j: neighbors |= {(4+0j, dim+1), (4+1j, dim+1), (4+2j, dim+1), (4+3j, dim+1), (4+4j, dim+1)}
                    case 1j: neighbors |= {(0+0j, dim+1), (1+0j, dim+1), (2+0j, dim+1), (3+0j, dim+1), (4+0j, dim+1)}
                    case -1j: neighbors |= {(0+4j, dim+1), (1+4j, dim+1), (2+4j, dim+1), (3+4j, dim+1), (4+4j, dim+1)}
            elif nb.real < 0: neighbors.add((1+2j, dim-1))
            elif nb.real > 4: neighbors.add((3+2j, dim-1))
            elif nb.imag < 0: neighbors.add((2+1j, dim-1))
            elif nb.imag > 4: neighbors.add((2+3j, dim-1))
            else: continue
            neighbors.remove((nb, dim))
        return neighbors
        
    def draw(self):
        dim = {d for _, d in self.bugs}
        for d in range(min(dim), max(dim)+1):
            print(f'Depth {d}:')
            state_string = ''
            for r in range(5):
                for c in range(5):
                    if r == 2 and c == 2: state_string += '?'
                    elif (c+r*1j, d) in self.bugs: state_string += '#'
                    else: state_string += '.'
                state_string += '\n'
            print(state_string)

    def evolve(self):
        next_bugs = set()
        all_neighbors = {nb for b in self.bugs for nb in self.get_neighbors(b)} - self.bugs
        for b in self.bugs:
            if len(self.get_neighbors(b) & self.bugs) == 1: next_bugs.add(b)
        for nb in all_neighbors:
            if 1 <= len(self.get_neighbors(nb) & self.bugs) <= 2: next_bugs.add(nb)
        self.bugs = next_bugs

#
# Process input
#
with open('day 24/input.txt') as file:
    map_string = file.read()
    eris_model = ErisModel(map_string)
    recursive_eris_model = RecursiveErisModel(map_string)

#
# Puzzle 1
#
i = 0
seen = set()
while not eris_model.state in seen:
    seen.add(eris_model.state)
    eris_model.evolve()

print(f'Puzzle 1 solution is: {eris_model.state} (after {len(seen)} iterations)')

#
# Puzzle 2
#
for i in range(200):
    recursive_eris_model.evolve()

print(f'Puzzle 2 solution is: {len(recursive_eris_model.bugs)}')