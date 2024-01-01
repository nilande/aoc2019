import re
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

class Inventory:
    def __init__(self) -> None:
        self.dictionary = {}
        self.contents = 0

    def __repr__(self) -> str:
        return ''.join([k[0] for k, v in self.dictionary.items() if v & self.contents])

    def process_line(self, line: str):
        items = re.findall(r'You take the (.*)\.', line)
        if len(items) == 1:
            item = items[0]
            if not item in self.dictionary:
                self.dictionary[item] = 1 << len(self.dictionary)
            self.contents |= self.dictionary[item]

        items = re.findall(r'You drop the (.*)\.', line)
        if len(items) == 1:
            item = items[0]
            self.contents &= ~self.dictionary[item]

    def exchange_items(self, to_contents: int):
        drops = [f'drop {k}' for k, v in self.dictionary.items() if v & self.contents & ~to_contents]
        takes = [f'take {k}' for k, v in self.dictionary.items() if v & to_contents & ~self.contents]
        return drops + takes

#
# Worker processes
#
def computer_main(conn):
    """Main function for the process running the computer. Communicating with other processes using a Pipe object"""
    with open('day 25/input.txt') as file:
        program_string = file.read().strip()
    computer = IntcodeComputer(program_string)
    computer.expand_memory(1000)
    computer.execute(conn)
    conn.close()

#
# Helper function
#
def readline(conn: Pipe) -> tuple:
    line = ''
    while line[-1:] != '\n':
        line += chr(conn.recv())
    return line[:-1]

def sendline(conn: Pipe, string: str) -> None:
    for c in string+'\n': conn.send(ord(c))

#
# Main function
#
if __name__ == "__main__":
    conn, child_conn = Pipe()
    p = Process(target=computer_main, args=(child_conn,))
    p.start()

    with open('day 25/commands.txt') as file:
        commands = file.read().splitlines()

    inventory = Inventory()

    # Automate collection of items
    while len(commands) > 0:
        if not conn.poll(0.1):
            command = commands.pop(0)
            print(f'> {command}')
            sendline(conn, command)
        else:
            line = readline(conn)
            inventory.process_line(line)
            print(line)

    # Loop through all possible inventory combinations
    i = 1
    commands = inventory.exchange_items(i) + ['north']
    while True:
        if not p.is_alive(): break
        elif not conn.poll(0.1):
            if len(commands) > 0:
                command = commands.pop(0)
                print(f'> {command}')
                sendline(conn, command)
            elif i < 255:
                i += 1
                commands = inventory.exchange_items(i) + ['north']
            else:
                command = input(f'> ')
                sendline(conn, command)
        else:
            line = readline(conn)
            inventory.process_line(line)
            print(line)

    p.join()
