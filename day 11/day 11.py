#
# Classes
#
class PaintColors:
    BLACK = 0
    WHITE = 1

class TurnDirection:
    LEFT = 0
    RIGHT = 1

class IntcodeComputer:
    def __init__(self, program_string: str):
        self.program = list(map(int, program_string.split(',')))
        self.program_backup = self.program.copy()
        self.instr_ptr = 0
        self.rel_base = 0
        self.completed = False

    def expand_memory(self, size: int):
        self.program.extend([0] * size)

    def reset(self):
        self.program = self.program_backup.copy()
        self.instr_ptr = 0
        self.rel_base = 0
        self.completed = False

    def has_completed(self):
        return self.completed

    # Fetches a value from the program at position 'pos' using parameter mode 'mode'
    def fetch(self, pos: int, param_mode: int, rel_base: int):
        match param_mode:
            case 0: return self.program[self.program[pos]]              # Position mode
            case 1: return self.program[pos]                            # Absolute mode
            case 2: return self.program[rel_base + self.program[pos]]   # Relative mode

    # Stores a value in the program at position 'pos' using parameter mode 'mode'
    def stor(self, pos: int, param_mode: int, rel_base: int, val: int):
        match param_mode:
            case 0: self.program[self.program[pos]] = val               # Position mode
            case 1: self.program[pos] = val                             # Absolute mode
            case 2: self.program[rel_base + self.program[pos]] = val    # Relative mode

    # Executes the program, with given input. Return output value
    def execute(self, input_val):
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
                    self.stor(self.instr_ptr + 1, param_mode % 10, self.rel_base, int(input_val))
                    self.instr_ptr += 2
                case 4:     # Output data
                    output = self.fetch(self.instr_ptr + 1, param_mode % 10, self.rel_base)
                    self.instr_ptr += 2
                    return output
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
                    return
                case _:
                    print(f'Error: Unknown opcode {op_code}... aborting.')
                    exit()

#
# Functions
#
def get_set_string(white_panels: set):
    rows = [int(x.imag) for x in white_panels]
    cols = [int(x.real) for x in white_panels]
    set_string = ''
    for r in range(max(rows), min(rows)-1, -1):
        for c in range(min(cols), max(cols)+1):
            set_string += chr(9608) if complex(c, r) in white_panels else ' '
        set_string += '\n'

    return set_string


#
# Process input
#
with open('day 11/input.txt') as file:
    computer = IntcodeComputer(file.read().strip())

#
# Puzzle 1
#
computer.expand_memory(1000)

# Represent where we are and our direction as complex numbers
pos = 0
dir = 1j

# All panels are black to start with -> white panels is an empty set
white_panels = set()
painted = set()

instr_ptr = 0
while True:
    # Determine color of tile under robot
    if pos in white_panels: input_val = PaintColors.WHITE
    else: input_val = PaintColors.BLACK

    # Execute the program to determine new color
    color = computer.execute(input_val)
    if computer.has_completed(): break

    # Determine paint color and paint the panel
    match color:
        case PaintColors.BLACK: 
            if pos in white_panels: white_panels.remove(pos)
        case PaintColors.WHITE: white_panels.add(pos)
    painted.add(pos)

    # Continue executing the program to determine turn direction
    direction = computer.execute(None)
    match direction:
        case TurnDirection.LEFT: dir *= 1j
        case TurnDirection.RIGHT: dir *= -1j
    pos += dir

print(f'Puzzle 1 solution is: {len(painted)}')

#
# Puzzle 2
#
computer.reset()
computer.expand_memory(1000)

# Represent where we are and our direction as complex numbers
pos = 0
dir = 1j

# For Puzzle 2, we make sure to start on a single white tile
white_panels = set([0+0j])

instr_ptr = 0
while True:
    # Determine color of tile under robot
    if pos in white_panels: input_val = PaintColors.WHITE
    else: input_val = PaintColors.BLACK

    # Execute the program to determine new color
    color = computer.execute(input_val)
    if computer.has_completed(): break

    # Determine paint color and paint the panel
    match color:
        case PaintColors.BLACK: 
            if pos in white_panels: white_panels.remove(pos)
        case PaintColors.WHITE: white_panels.add(pos)

    # Continue executing the program to determine turn direction
    direction = computer.execute(None)
    match direction:
        case TurnDirection.LEFT: dir *= 1j
        case TurnDirection.RIGHT: dir *= -1j
    pos += dir

print(f'Puzzle 1 solution is:\n{get_set_string(white_panels)}')