import time
from multiprocessing import Process, Pipe

#
# Classes
#
class IntcodeComputer:
    """This is a version of the Intcode computer that expects to be run in a separate process, and communicate using a Pipe"""
    def __init__(self, program_string: str, conn: Pipe, address: int) -> None:
        self.program = list(map(int, program_string.split(',')))
        self.conn = conn
        self.send_buffer = []
        self.recv_buffer = [ address ]
        self.address = address
        self.idle_timer = None

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

    def send(self, data: int) -> None:
        """Use the computer's Pipe object to send data"""
        self.idle_timer = None # Reset idle timer
        self.send_buffer.append(data)
        if len(self.send_buffer) > 2: # Send data every 3rd instruction
            self.conn.send(self.send_buffer)
            self.send_buffer.clear()

    def recv(self) -> int:
        """Use the computer's Pipe object to receive data"""
        if len(self.recv_buffer) > 0:
            self.idle_timer = None # Reset idle timer
            return self.recv_buffer.pop(0)
        elif self.conn.poll(0.02):
            self.idle_timer = None # Reset idle timer
            self.recv_buffer = self.conn.recv()
            return self.recv_buffer.pop(0)
        else:
            if self.idle_timer is None: self.idle_timer = time.time()
            idle_time = time.time() - self.idle_timer
            if idle_time > 0.1:
                # print(f'Warning: Node {self.address} has been idle for {idle_time:.2f} seconds')
                self.conn.send((-1, self.address, self.idle_timer)) # Send request for help packet to get latest value from NAT
                self.idle_timer = None
            return -1

    def execute(self) -> None:
        """Executes the program"""
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
                    self.stor(instr_ptr + 1, param_mode % 10, rel_base, self.recv())
                    instr_ptr += 2
                case 4:     # Output data
                    self.send(self.fetch(instr_ptr + 1, param_mode % 10, rel_base))
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
    with open('day 23/input.txt') as file:
        program_string = file.read().strip()

    # Initialize the computer by also assigning the address received as the first entry in the Pipe
    computer = IntcodeComputer(program_string, conn, conn.recv())
    computer.expand_memory(100)

    # Start the program
    computer.execute()
    conn.close()

#
# Main function
#
if __name__ == "__main__":
    #
    # Puzzle 1 and 2
    #
    connections = []
    processes = []
    for i in range(50):
        conn, child_conn = Pipe()
        p = Process(target=computer_main, args=(child_conn,))
        p.start()
        conn.send(i)
        processes.append(p)
        connections.append(conn)

    # Initialize idle timers such that noone indicates idle
    latest_nat_update = time.time()
    idle_timers = [ latest_nat_update-1 ] * 50

    print(f'Starting communication: ', end='')

    # Keep track of latest NAT package(s)
    nat_x = None
    nat_y = None
    nat_ys = []
    while True:
        for c in connections:
            if c.poll():
                dest, x, y = c.recv()
                if 0 <= dest < 50:  # "Normal" packet
                    connections[dest].send([x, y])
                elif dest == 255:   # NAT packet
                    if nat_y is None:
                        print(f'\nPuzzle 1 solution is: {y}')
                    nat_x = x
                    nat_y = y
                elif dest == -1:    # "Idle node" packet of structure (-1, node id, idle timer)
                    idle_timers[x] = y
                    if all(x > latest_nat_update for x in idle_timers):
                        connections[0].send([nat_x, nat_y])
                        latest_nat_update = time.time()

                        # Same Y value has been sent twice in a row (Puzzle 2 solution)
                        nat_ys.append(nat_y)
                        if len(nat_ys) >= 2 and nat_ys[-2] == nat_ys[-1]:
                            print(f'Puzzle 2 solution is: {nat_y}')
                            for p in processes: p.terminate()
                            exit()

    # p.join()
