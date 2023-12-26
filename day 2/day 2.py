#
# Functions
#
def execute_program(program: list, noun: int, verb: int):
    program[1] = noun
    program[2] = verb
    instr_ptr = 0
    while True:
        match program[instr_ptr]:
            case 1: # Addition
                program[program[instr_ptr + 3]] = program[program[instr_ptr + 1]] + program[program[instr_ptr + 2]]
                instr_ptr += 4
            case 2: # Multiplication
                program[program[instr_ptr + 3]] = program[program[instr_ptr + 1]] * program[program[instr_ptr + 2]]
                instr_ptr += 4
            case 99: # End of program
                break

#
# Process input
#
with open('day 2/input.txt', 'r') as file:
    program_original = list(map(int, file.read().split(',')))

#
# Puzzle 1
#
program = program_original.copy()
execute_program(program, 12, 2)

print(f'Puzzle 1 solution is: {program[0]}')

#
# Puzzle 2
#
target = 19690720
for noun in range(100):
    for verb in range(100):
        program = program_original.copy()
        execute_program(program, noun, verb)
        if program[0] == target:
            print(f'Puzzle 2 solution is: {100 * noun + verb}')
