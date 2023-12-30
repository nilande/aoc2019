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
    """Lists the available tile types in the scaffold map"""
    SCAFFOLD = '#'

class ScaffoldMap:
    """Contains all information about known whereabouts of different tile types"""
    def __init__(self) -> None:
        self.tiles = {
            TileType.SCAFFOLD: set()
        }

    def load_camera_frame(self, frame: str, robot_pos: complex | None = None) -> None:
        width = frame.find('\n')+1

        # If we know the robot position, we can use this info to calculate a camera view offset
        if robot_pos is not None: 
            i = max(frame.find('^'), frame.find('>'), frame.find('v'), frame.find('<'))
            offset = robot_pos - i%width - i//width*1j
        else: offset = 0+0j

        # Walk through the image
        for i in range(len(frame)):
            i_pos = i%width + i//width*1j + offset
            match frame[i]:
                case TileType.SCAFFOLD: self.tiles[TileType.SCAFFOLD].add(i_pos)
                case '^':
                    self.tiles[TileType.SCAFFOLD].add(i_pos)
                    self.robot_pos = i_pos
                    self.robot_dir = -1j
                case '>':
                    self.tiles[TileType.SCAFFOLD].add(i_pos)
                    self.robot_pos = i_pos
                    self.robot_dir = 1+0j
                case 'v':
                    self.tiles[TileType.SCAFFOLD].add(i_pos)
                    self.robot_pos = i_pos
                    self.robot_dir = 1j
                case '<':
                    self.tiles[TileType.SCAFFOLD].add(i_pos)
                    self.robot_pos = i_pos
                    self.robot_dir = -1+0j
    
    def get_journey(self) -> list:
        journey = []
        pos = self.robot_pos
        explored = {pos}
        dir = self.robot_dir

        while True:
            next_steps = {pos+1, pos-1, pos+1j, pos-1j} & scaffold_map.tiles[TileType.SCAFFOLD] - explored
            if len(next_steps) == 0: break
            turn = (next(iter(next_steps)) - pos) / dir
            journey.append(TURN_COMMAND[turn])
            dir = dir * turn
            steps = 0
            while pos + dir in scaffold_map.tiles[TileType.SCAFFOLD]:
                pos += dir
                explored.add(pos)
                steps += 1
            journey.append(str(steps))

        return journey


#
# Worker processes
#
def computer_main(conn):
    """Main function for the process running the computer. Communicating with other processes using a Pipe object"""
    with open('day 17/input.txt') as file:
        program_string = file.read().strip()
    computer = IntcodeComputer(program_string)
    computer.expand_memory(10000)
    computer.execute(conn)
    conn.close()

def modified_computer_main(conn):
    with open('day 17/input.txt') as file:
        program_string = file.read().strip()
    computer = IntcodeComputer(program_string)
    computer.program[0] = 2 # Alter the program to accept commands
    computer.expand_memory(10000)
    computer.execute(conn)
    conn.close()

#
# Translation dictionaries
#
TURN_COMMAND = {
    0-1j: 'L',
    0+1j: 'R'
}

#
# Helper function
#
def get_camera_frame(conn: Pipe) -> str:
    frame = ''
    ret_val = None
    while frame[-2:] != '\n\n':
        recv = conn.recv()
        if recv < 256: frame += chr(recv)
        else:
            ret_val = recv
            return frame, ret_val
    return frame[:-1], ret_val

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

    scaffold_map = ScaffoldMap()
    frame, _ = get_camera_frame(conn)
    print(frame)
    scaffold_map.load_camera_frame(frame)
    
    # Calculate the intersections' alignment parameters in the initial camera view
    acc = 0
    for s in scaffold_map.tiles[TileType.SCAFFOLD]:
        if len({s+1, s-1, s+1j, s-1j} & scaffold_map.tiles[TileType.SCAFFOLD]) > 2: acc += int(s.real)*int(s.imag)
    print(f'Puzzle 1 solution is: {acc}')

    p.join()

    input('Press ENTER to move to Puzzle 2...')

    #
    # Puzzle 2
    #
    journey = scaffold_map.get_journey()
    journey_len = len(journey)
    journey_pattern = ','.join(journey)

    # Identify patterns, i.e. subsets of length 2-10 of the journey that occurs more than once
    sub_journeys = {}
    for i in range(journey_len):
        for j in range(i+1, journey_len+1):
            sub_journey = tuple(journey[i:j])
            sub_journeys.setdefault(sub_journey, 0)
            sub_journeys[sub_journey] += 1
    patterns = [a for a, b in sub_journeys.items() if b > 1 and 1 < len(a) <= 10]
    
    main_routine_charset = {'A', 'B', 'C', ','}
    for a in range(len(patterns)):
        # Let's chose pattern A so that the it must match the start of the journey
        if tuple(patterns[a][:2]) != tuple(journey[:2]): continue
        a_len = len(patterns[a])
        a_pattern = ','.join(patterns[a])
        if len(a_pattern) > 20: continue
        for b in range(len(patterns)-1):
            if a == b: continue
            b_len = len(patterns[b])
            b_pattern = ','.join(patterns[b])
            if len(b_pattern) > 20: continue
            for c in range(b+1, len(patterns)):
                if a == c or b == c: continue
                c_len = len(patterns[c])
                c_pattern = ','.join(patterns[c])
                if len(c_pattern) > 20: continue
                main_routine = journey_pattern.replace(a_pattern, 'A').replace(b_pattern, 'B').replace(c_pattern, 'C')
                if len(main_routine) <= 20 and all(x in main_routine_charset for x in main_routine):
                    print(f'\nSolution found:\nMain routine: {main_routine}\nFunction A: {a_pattern}\nFunction B: {b_pattern}\nFunction C: {c_pattern}\n')
                    break
            else: continue
            break
        else: continue
        break
    
    # Now we are ready to run the computer
    conn, child_conn = Pipe()
    p = Process(target=modified_computer_main, args=(child_conn,))
    p.start()

    send_string = f'{main_routine}\n{a_pattern}\n{b_pattern}\n{c_pattern}\ny\n'
    for c in send_string: conn.send(ord(c))

    print('\033[2J', end='')

    ret_val = None
    while ret_val is None:
        frame, ret_val = get_camera_frame(conn)
        print(frame + '\033[43A', end='')

    print(f'\033[43B\nPuzzle 2 solution is: {ret_val}')

    # Terminate instead of join since the program runs a never ending loop
    p.terminate()
