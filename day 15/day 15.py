import time
from multiprocessing import Process, Pipe
from collections import deque

#
# Classes
#
class IntcodeComputer:
    """This is a version of the Intcode computer that expects to be run in a separate process, and communicate using a Pipe"""
    def __init__(self, program_string: str) -> None:
        self.program = list(map(int, program_string.split(',')))

    def expand_memory(self, size: int) -> None:
        self.program.extend([0] * size)

    def fetch(self, pos: int, param_mode: int, rel_base: int) -> int:
        """Fetches a value from the program at position 'pos' using parameter mode 'mode'"""
        match param_mode:
            case 0: return self.program[self.program[pos]]              # Position mode
            case 1: return self.program[pos]                            # Absolute mode
            case 2: return self.program[rel_base + self.program[pos]]   # Relative mode

    def stor(self, pos: int, param_mode: int, rel_base: int, val: int) -> None:
        """Stores a value in the program at position 'pos' using parameter mode 'mode'"""
        match param_mode:
            case 0: self.program[self.program[pos]] = val               # Position mode
            case 1: self.program[pos] = val                             # Absolute mode
            case 2: self.program[rel_base + self.program[pos]] = val    # Relative mode

    def execute(self, conn: Pipe) -> None:
        """Executes the program, with communication with host process happening through Pipe object"""
        instr_ptr = 0
        rel_base = 0

        while True:
            op_code = self.program[instr_ptr] % 100
            param_mode = self.program[instr_ptr] // 100

            match op_code:
                case 1:     # Addition
                    self.stor(instr_ptr + 3, param_mode % 1000 // 100, rel_base, self.fetch(instr_ptr + 1, param_mode % 10, rel_base) + self.fetch(instr_ptr + 2, param_mode % 100 // 10, rel_base))
                    instr_ptr += 4
                case 2:     # Multiplication
                    self.stor(instr_ptr + 3, param_mode % 1000 // 100, rel_base, self.fetch(instr_ptr + 1, param_mode % 10, rel_base) * self.fetch(instr_ptr + 2, param_mode % 100 // 10, rel_base))
                    instr_ptr += 4
                case 3:     # Input data
                    self.stor(instr_ptr + 1, param_mode % 10, rel_base, conn.recv())
                    instr_ptr += 2
                case 4:     # Output data
                    conn.send(self.fetch(instr_ptr + 1, param_mode % 10, rel_base))
                    instr_ptr += 2
                case 5:     # Jump if true
                    if self.fetch(instr_ptr + 1, param_mode % 10, rel_base) != 0: instr_ptr = self.fetch(instr_ptr + 2, param_mode % 100 // 10, rel_base)
                    else: instr_ptr += 3
                case 6:     # Jump if false
                    if self.fetch(instr_ptr + 1, param_mode % 10, rel_base) == 0: instr_ptr = self.fetch(instr_ptr + 2, param_mode % 100 // 10, rel_base)
                    else: instr_ptr += 3
                case 7:     # Less than
                    if self.fetch(instr_ptr + 1, param_mode % 10, rel_base) < self.fetch(instr_ptr + 2, param_mode % 100 // 10, rel_base):
                        self.stor(instr_ptr + 3, param_mode % 1000 // 100, rel_base, 1)
                    else:
                        self.stor(instr_ptr + 3, param_mode % 1000 // 100, rel_base, 0)
                    instr_ptr += 4
                case 8:     # Equals
                    if self.fetch(instr_ptr + 1, param_mode % 10, rel_base) == self.fetch(instr_ptr + 2, param_mode % 100 // 10, rel_base):
                        self.stor(instr_ptr + 3, param_mode % 1000 // 100, rel_base, 1)
                    else:
                        self.stor(instr_ptr + 3, param_mode % 1000 // 100, rel_base, 0)
                    instr_ptr += 4
                case 9:     # Change relative base
                    rel_base += self.fetch(instr_ptr + 1, param_mode % 10, rel_base)
                    instr_ptr += 2
                case 99:    # Break
                    return
                case _:
                    print(f'Error: Unknown opcode {op_code}... aborting.')
                    return

class TileType:
    """Lists the available tile types in the section map"""
    WALL = 0
    FLOOR = 1
    OXYGEN_SYSTEM = 2
    TO_EXPLORE = 3
    ORIGIN = 4

class SectionMap:
    """Contains all information about known whereabouts of different tile types"""
    def __init__(self) -> None:
        self.tiles = {
            TileType.WALL: set(),
            TileType.FLOOR: set(),
            TileType.OXYGEN_SYSTEM: set(),
            TileType.TO_EXPLORE: set(),
            TileType.ORIGIN: { 0+0j }
        }
        self.update_tile(0+0j, TileType.FLOOR)

    def draw(self, droid_position: complex = None) -> None:
        """Draw the map by printing to STDOUT"""
        rows = [ int(x.imag) for x in (self.tiles[TileType.FLOOR] | self.tiles[TileType.WALL] | self.tiles[TileType.TO_EXPLORE]) ]
        cols = [ int(x.real) for x in (self.tiles[TileType.FLOOR] | self.tiles[TileType.WALL] | self.tiles[TileType.TO_EXPLORE]) ]
        set_string = f'\033[2J'
        for y in range(min(rows), max(rows)+1):
            for x in range(min(cols), max(cols)+1):
                tile = x+y*1j
                if tile == droid_position: set_string += chr(0x25aa)
                elif tile in self.tiles[TileType.OXYGEN_SYSTEM]: set_string += 'O'
                elif tile in self.tiles[TileType.FLOOR]: set_string += chr(0x2591)
                elif tile in self.tiles[TileType.WALL]: set_string += chr(0x2588)
                elif tile in self.tiles[TileType.TO_EXPLORE]: set_string += '?'
                else: set_string += ' '
            set_string += '\n'
        print(set_string)

    def update_tile(self, pos: complex, tile_type: TileType) -> None:
        """Update information about what is known about a given tile"""
        if pos in self.tiles[TileType.TO_EXPLORE]: self.tiles[TileType.TO_EXPLORE].remove(pos)
        add_to_explore = {pos+1, pos-1, pos+1j, pos-1j} - (self.tiles[TileType.FLOOR] | self.tiles[TileType.WALL])
        match tile_type:
            case TileType.WALL: self.tiles[TileType.WALL].add(pos)
            case TileType.FLOOR:
                self.tiles[TileType.FLOOR].add(pos)
                self.tiles[TileType.TO_EXPLORE] |= add_to_explore
            case TileType.OXYGEN_SYSTEM:
                self.tiles[TileType.OXYGEN_SYSTEM].add(pos)
                self.tiles[TileType.FLOOR].add(pos)
                self.tiles[TileType.TO_EXPLORE] |= add_to_explore

    def get_path_to_tile_type(self, pos: complex, tile_type: TileType) -> list:
        """Find the shortest path to a tile of a given tile type"""
        if len(self.tiles[tile_type]) == 0: return None     # If there are no such tiles to be found, leave the function

        queue = deque([ (pos, deque()) ])
        explored = set()
        while len(queue) > 0:
            current_pos, current_path = queue.popleft()
            if current_pos in explored: continue
            explored.add(current_pos)
            current_path.append(current_pos)
            if current_pos in self.tiles[tile_type]: break  # End the search when the requested tile type has been found
            to_explore = list({current_pos+1, current_pos-1, current_pos+1j, current_pos-1j} - self.tiles[TileType.WALL])
            for next_pos in to_explore: queue.append((next_pos, current_path.copy()))

        # Assemble a list of steps needed to take to arrive at the given tile type
        assembled_directions = []
        for i in range(len(current_path)-1):
            assembled_directions.append(current_path[i+1] - current_path[i])

        return assembled_directions
    
    def get_steps_to_fill_map(self) -> int:
        queue = deque([(self.tiles[TileType.OXYGEN_SYSTEM].pop(), 0)])
        explored = set()
        while len(queue) > 0:
            pos, steps = queue.popleft()
            if pos in explored: continue
            last_steps = steps
            explored.add(pos)
            to_explore = list({pos+1, pos-1, pos+1j, pos-1j} & self.tiles[TileType.FLOOR])
            for next_pos in to_explore: queue.append((next_pos, steps + 1))

        return last_steps

#
# Worker processes
#
def computer_main(conn):
    """Main function for the process running the computer. Communicating with other processes using a Pipe object"""
    with open('day 15/input.txt') as file:
        program_string = file.read().strip()
    computer = IntcodeComputer(program_string)
    computer.execute(conn)
    conn.close()

#
# Translation dictionaries
#
TO_COMPUTER = {
    -1j: 1,     # North
    1j: 2,      # South
    -1+0j: 3,   # West
    1+0j: 4     # East
}

#
# Main function
#
if __name__ == "__main__":
    conn, child_conn = Pipe()
    p = Process(target=computer_main, args=(child_conn,))
    p.start()

    section_map = SectionMap()
    current_position = 0+0j
    walk_queue = []

    step_counter = 0
    while True:
        if step_counter % 25 == 0: section_map.draw(current_position)
        if len(walk_queue) == 0: walk_queue = section_map.get_path_to_tile_type(current_position, TileType.TO_EXPLORE)
        if walk_queue == None: break
        movement_cmd = walk_queue.pop(0)
        conn.send(TO_COMPUTER[movement_cmd])
        droid_response = conn.recv()

        match droid_response:
            case TileType.WALL:
                walk_queue = []
                section_map.update_tile(current_position + movement_cmd, droid_response)
            case _:
                current_position += movement_cmd
                section_map.update_tile(current_position, droid_response)

        step_counter += 1
        time.sleep(0.001)
    # Terminate instead of join since the program runs a never ending loop
    p.terminate()
    # p.join()

    section_map.draw(0+0j)
    print(f'Puzzle 1 solution is: {len(section_map.get_path_to_tile_type(0+0j, TileType.OXYGEN_SYSTEM))}')

    print(f'Puzzle 2 solution is: {section_map.get_steps_to_fill_map()}')

