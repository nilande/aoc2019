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
    with open('day 19/input.txt') as file:
        program_string = file.read().strip()
    computer = IntcodeComputer(program_string)
    computer.expand_memory(100)
    while True:
        computer.backup()
        computer.execute(conn)
        computer.restore()
    conn.close()

#
# Main function
#
if __name__ == "__main__":
    #
    # Puzzle 1
    #
    conn, child_conn = Pipe()
    p = Process(target=computer_main, args=(child_conn,))
    p.start()

    acc = 0
    beam_view = ''
    for y in range(50):
        for x in range(50):
            conn.send(x)
            conn.send(y)
            if conn.recv() == 1:
                beam_view += '#'
                acc += 1
                puzzle2_start = (x, y)
            else:
                beam_view += '.'
        beam_view += '\n'

    print(beam_view)

    print(f'Puzzle 1 solution is: {acc}')

    #
    # Puzzle 2
    #
    x, y = puzzle2_start
    diag_len = 0
    start_points = []
    while diag_len < 100:
        while True: # Move down
            y += 1
            conn.send(x)
            conn.send(y)
            if conn.recv() == 0: break

        diag_len = 0
        y -= 1
        start_points.append((x, y))
        while True: # Move diagonally up
            x += 1
            y -= 1
            diag_len += 1
            conn.send(x)
            conn.send(y)
            if conn.recv() == 0: break
        x -= 1
        y += 1

    # Fine grained search between the last two diagonal searches
    for x in range(start_points[-2][0], start_points[-1][0]):
        for y in range(start_points[-2][1], start_points[-1][1]):
            for i in range(0, 100, 99):
                conn.send(x+i)
                conn.send(y-i)
                if conn.recv() == 0:
                    break
            else:
                y -= 99
                break
        else: continue
        break

    print(f'Puzzle 2 solution is: {x*10000 + y} (x={x}, y={y})')

    p.terminate()
    p.join()
