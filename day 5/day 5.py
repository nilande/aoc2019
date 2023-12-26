#
# Functions
#
# Fetches a value from the program 'program' at position 'pos' using parameter mode 'mode'
def fetch(program, pos, mode):
    match mode:
        case 0: # Position mode
            return program[program[pos]]
        case 1: # Immediate mode
            return program[pos]
        case _:
            print(f'Error: No such fetch mode: {mode}. Aborting.')
            exit()
    
def execute_program(program: list):
    instr_ptr = 0
    while True:
        opcode = program[instr_ptr] % 100     # Extract operand
        mode = program[instr_ptr] // 100      # Extract parameter mode

        match opcode:
            case 1: # Addition
                program[program[instr_ptr + 3]] = fetch(program, instr_ptr + 1, mode % 10) + fetch(program, instr_ptr + 2, mode % 100 // 10)
                instr_ptr += 4
            case 2: # Multiplication
                program[program[instr_ptr + 3]] = fetch(program, instr_ptr + 1, mode % 10) * fetch(program, instr_ptr + 2, mode % 100 // 10)
                instr_ptr += 4
            case 3: # Input data from STDIN
                program[program[instr_ptr + 1]] = int(input())
                instr_ptr += 2
            case 4: # Output data to STDOUT
                print(fetch(program, instr_ptr + 1, mode % 10))
                instr_ptr += 2
            case 5: # Jump if true
                if fetch(program, instr_ptr + 1, mode % 10) != 0: instr_ptr = fetch(program, instr_ptr + 2, mode % 100 // 10)
                else: instr_ptr += 3
            case 6: # Jump if false
                if fetch(program, instr_ptr + 1, mode % 10) == 0: instr_ptr = fetch(program, instr_ptr + 2, mode % 100 // 10)
                else: instr_ptr += 3
            case 7: # Less than
                if fetch(program, instr_ptr + 1, mode % 10) < fetch(program, instr_ptr + 2, mode % 100 // 10):
                    program[program[instr_ptr + 3]] = 1
                else:
                    program[program[instr_ptr + 3]] = 0
                instr_ptr += 4
            case 8: # Equals
                if fetch(program, instr_ptr + 1, mode % 10) == fetch(program, instr_ptr + 2, mode % 100 // 10):
                    program[program[instr_ptr + 3]] = 1
                else:
                    program[program[instr_ptr + 3]] = 0
                instr_ptr += 4
            case 99: # End of program
                break
            case _: #Error
                print(f'Error: No such opcode: {opcode}. Aborting.')
                exit()

#
# Process input
#
with open('day 5/input.txt', 'r') as file:
    program_original = list(map(int, file.read().split(',')))

#
# Puzzle 1 and 2 (input dependent)
#
program = program_original.copy()
execute_program(program)

#print(program)