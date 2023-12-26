import time
#
# Classes
#
class TileType:
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4

class IntcodeComputer:
    def __init__(self, program_string: str) -> None:
        self.program = list(map(int, program_string.split(',')))
        self.program_backup = self.program.copy()
        self.instr_ptr = 0
        self.rel_base = 0
        self.completed = False

    def expand_memory(self, size: int) -> None:
        self.program.extend([0] * size)

    def reset(self) -> None:
        self.program = self.program_backup.copy()
        self.instr_ptr = 0
        self.rel_base = 0
        self.completed = False

    def has_completed(self) -> bool:
        return self.completed

    # Fetches a value from the program at position 'pos' using parameter mode 'mode'
    def fetch(self, pos: int, param_mode: int, rel_base: int) -> int:
        match param_mode:
            case 0: return self.program[self.program[pos]]              # Position mode
            case 1: return self.program[pos]                            # Absolute mode
            case 2: return self.program[rel_base + self.program[pos]]   # Relative mode

    # Stores a value in the program at position 'pos' using parameter mode 'mode'
    def stor(self, pos: int, param_mode: int, rel_base: int, val: int) -> None:
        match param_mode:
            case 0: self.program[self.program[pos]] = val               # Position mode
            case 1: self.program[pos] = val                             # Absolute mode
            case 2: self.program[rel_base + self.program[pos]] = val    # Relative mode

    # Executes the program, with given input. Return output value
    def execute(self, input_val: int) -> list:
        outputs = []

        while True:
            op_code = self.program[self.instr_ptr] % 100
            param_mode = self.program[self.instr_ptr] // 100

            match op_code:
                case 1:     # Addition
                    self.stor(self.instr_ptr + 3, param_mode % 1000 // 100, self.rel_base, self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base) + self.fetch(self.instr_ptr + 2, param_mode % 100 // 10, self.rel_base))
                    self.instr_ptr += 4
                case 2:     # Multiplication
                    self.stor(self.instr_ptr + 3, param_mode % 1000 // 100, self.rel_base, self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base) * self.fetch(self.instr_ptr + 2, param_mode % 100 // 10, self.rel_base))
                    self.instr_ptr += 4
                case 3:     # Input data
                    if input_val == None: return outputs    # Return control to calling function to await new input
                    self.stor(self.instr_ptr + 1, param_mode % 10, self.rel_base, int(input_val))
                    input_val = None                        # Reset input to make sure control is returned before next input
                    self.instr_ptr += 2
                case 4:     # Output data
                    outputs.append(self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base))
                    self.instr_ptr += 2
                case 5:     # Jump if true
                    if self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base) != 0: self.instr_ptr = self.fetch(self.instr_ptr + 2, param_mode % 100 // 10, self.rel_base)
                    else: self.instr_ptr += 3
                case 6:     # Jump if false
                    if self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base) == 0: self.instr_ptr = self.fetch(self.instr_ptr + 2, param_mode % 100 // 10, self.rel_base)
                    else: self.instr_ptr += 3
                case 7:     # Less than
                    if self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base) < self.fetch(self.instr_ptr + 2, param_mode % 100 // 10, self.rel_base):
                        self.stor(self.instr_ptr + 3, param_mode % 1000 // 100, self.rel_base, 1)
                    else:
                        self.stor(self.instr_ptr + 3, param_mode % 1000 // 100, self.rel_base, 0)
                    self.instr_ptr += 4
                case 8:     # Equals
                    if self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base) == self.fetch(self.instr_ptr + 2, param_mode % 100 // 10, self.rel_base):
                        self.stor(self.instr_ptr + 3, param_mode % 1000 // 100, self.rel_base, 1)
                    else:
                        self.stor(self.instr_ptr + 3, param_mode % 1000 // 100, self.rel_base, 0)
                    self.instr_ptr += 4
                case 9:     # Change relative base
                    self.rel_base += self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base)
                    self.instr_ptr += 2
                case 99:    # Break
                    self.completed = True
                    return outputs
                case _:
                    print(f'Error: Unknown opcode {op_code}... aborting.')
                    exit()

#
# Functions
#
def draw(tiles: dict):
    tile_color = ['\033[0m', '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']


    rows = [int(x.imag) for x in tiles.keys()]
    cols = [int(x.real) for x in tiles.keys()]
    set_string = ''
    for y in range(min(rows), max(rows)+1):
        for x in range(min(cols), max(cols)+1):
            match tiles[x+y*1j]:
                case TileType.EMPTY: set_string += ' ' * 3
                case TileType.WALL: set_string += chr(9608) * 3
                case TileType.BLOCK: set_string += tile_color[(x+y*3)%6+1] + chr(9618) * 3 + tile_color[0]
                case TileType.PADDLE: set_string += chr(9603) * 3
                case TileType.BALL: set_string += ' O '
        set_string += '\n'

    print(set_string)


#
# Process input
#
with open('day 13/input.txt') as file:
    computer = IntcodeComputer(file.read().strip())

#
# Puzzle 1
#
computer.expand_memory(1000)
ret_val = computer.execute(None)
tiles = {}
for i in range(0, len(ret_val), 3):
    x, y, tile_type = ret_val[i:i+3]
    tiles[x+y*1j] = tile_type
draw(tiles)

block_tiles = sum(1 for x in tiles.values() if x == 2)
print(f'Puzzle 1 solution is: {block_tiles}')

#
# Puzzle 2
#
computer.reset()
computer.expand_memory(1000)
computer.program[0] = 2
joystick_input = None
score = None

while not computer.has_completed():
    ret_val = computer.execute(joystick_input)

    for i in range(0, len(ret_val), 3):
        x, y, tile_type = ret_val[i:i+3]
        if x < 0:
            score = tile_type
            continue
        tiles[x+y*1j] = tile_type
        if tile_type == TileType.BALL: ball_x = x
        elif tile_type == TileType.PADDLE: paddle_x = x

    draw(tiles)

    block_tiles = sum(1 for x in tiles.values() if x == 2)
    print(f'Current score: {score}. Blocks left: {block_tiles}  \033[28A')

    joystick_input = ((paddle_x < ball_x) - (paddle_x > ball_x))

    time.sleep(0.02)

print(f'\033[28B\n\nPuzzle 2 solution is: {score}')