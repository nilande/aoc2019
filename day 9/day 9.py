#
# Classes
#
class IntcodeComputer:
    def __init__(self, program_string: str):
        self.program = list(map(int, program_string.split(',')))

    def expand_memory(self, size: int):
        self.program.extend([0] * size)

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

    # Executes the program with a given input vector
    def execute(self):
        # Initialize relative base
        rel_base = 0
        instr_ptr = 0

        # Step through program
        while True:
            op_code = self.program[instr_ptr] % 100   # Extract operand
            param_mode = self.program[instr_ptr] // 100   # Extract parameter modes

            match op_code:
                case 1:     # Addition
                    self.stor(instr_ptr + 3, param_mode % 1000 // 100, rel_base, self.fetch(instr_ptr + 1, param_mode % 10, rel_base) + self.fetch(instr_ptr + 2, param_mode % 100 // 10, rel_base))
                    instr_ptr += 4
                case 2:     # Multiplication
                    self.stor(instr_ptr + 3, param_mode % 1000 // 100, rel_base, self.fetch(instr_ptr + 1, param_mode % 10, rel_base) * self.fetch(instr_ptr + 2, param_mode % 100 // 10, rel_base))
                    instr_ptr += 4
                case 3:     # Input data
                    self.stor(instr_ptr + 1, param_mode % 10, rel_base, int(input('Input: ')))
                    instr_ptr += 2
                case 4:     # Output data
                    print(self.fetch(instr_ptr + 1, param_mode % 10, rel_base))
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


#
# Process input
#
with open('day 9/input.txt') as file:
    computer = IntcodeComputer(file.read().strip())

#
# Puzzle 1 and 2
#
computer.expand_memory(1000)
computer.execute()