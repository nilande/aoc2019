import functools
from multiprocessing import Process, Pipe

#
# Classes
#
class IntcodeComputer:
    """This is a version of the Intcode computer that expects to be run in a separate process, and communicate using a Pipe"""
    def __init__(self, program_string: str) -> None:
        self.program = list(map(int, program_string.split(',')))

    def expand_memory(self, size: int) -> None:
        """Enpand the program memory of the computer with 'size' values"""
        self.program.extend([0] * size)

    def backup(self) -> None:
        """Backup the current program memory of the computer (note: does not save instruction pointer or relative base)"""
        self.program_backup = self.program.copy()

    def restore(self) -> None:
        """Restore the program memory of the computer"""
        self.program = self.program_backup.copy()

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

#
# Worker processes
#
def computer_main(conn):
    """Main function for the process running the computer. Communicating with other processes using a Pipe object"""
    with open('day 21/input.txt') as file:
        program_string = file.read().strip()
    computer = IntcodeComputer(program_string)
    computer.expand_memory(1000)
    computer.backup()
    while True:
        computer.execute(conn)
        conn.send(-1) # Send reboot
        computer.restore()
    conn.close()

#
# Constants
#
INSTRUCTIONS = [
    ['AND', ['A', 'B', 'C', 'D', 'T', 'J'], ['T', 'J']],
    ['OR', ['A', 'B', 'C', 'D', 'T', 'J'], ['T', 'J']],
    ['NOT', ['A', 'B', 'C', 'D', 'T', 'J'], ['T', 'J']]
]

#
# Helper function
#
def readline(conn: Pipe) -> tuple:
    line = ''
    char = None
    while line[-1:] != '\n':
        char = conn.recv()
        if not 0 <= char < 256: return line, char
        line += chr(char)
    return line[:-1], None

def sendline(conn: Pipe, string: str) -> None:
    for c in string+'\n': conn.send(ord(c))

@functools.cache
def get_instruction(number: int) -> str:
    """Get the text instruction matching a value between 0-35"""
    i = INSTRUCTIONS[number % 3]
    number //= 3
    p1 = number % 6
    number //= 6
    p2 = number
    return f'{i[0]} {i[1][p1]} {i[2][p2]}'

def get_instructions(number: int) -> str:
    instructions = ''
    while number > 0:
        instructions += get_instruction(number % 36) + '\n'
        number //= 36
    return instructions

#
# Main function
#
if __name__ == "__main__":
    #
    # Both puzzles
    #
    # Puzzle 1 solution:
    # > NOT C T
    # > AND D T
    # > NOT A J
    # > OR T J
    # > WALK
    #
    # Puzzle 2 solution:
    # > NOT B J
    # > AND D J
    # > NOT C T
    # > AND D T
    # > AND H T
    # > OR T J
    # > NOT A T
    # > OR T J
    # > RUN
    #
    conn, child_conn = Pipe()
    p = Process(target=computer_main, args=(child_conn,))
    p.start()

    while True:
        print(readline(conn)[0])
        
        command = ''
        while command not in ('WALK', 'RUN'):
            command = input('> ')
            sendline(conn, command)
        while True:
            line, val = readline(conn)
            print(line)
            if val is not None:
                break
        if val != -1:
            print(f'Puzzle solution is: {val}')
            break

    p.kill()
