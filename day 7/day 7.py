# Fetches a value from the program 'program' at position 'pos' using parameter mode 'mode'
def fetch(program, pos, mode):
    if mode == 0:
        return program[program[pos]]
    elif mode == 1:
        return program[pos]

# Executes the program with a given input vector
def execute_pt1(program, inVec):
    opPos = 0
    inPos = 0 # Which value from the input vector to pick up

    # Step through program
    while True:
        opCode = program[opPos] % 100   # Extract operand
        modes = program[opPos] // 100   # Extract parameter modes

        if opCode == 1:                 # Addition
            program[program[opPos + 3]] = fetch(program, opPos + 1, modes % 10) + fetch(program, opPos + 2, modes % 100 // 10)
            opPos += 4
        elif opCode == 2:               # Multiplication
            program[program[opPos + 3]] = fetch(program, opPos + 1, modes % 10) * fetch(program, opPos + 2, modes % 100 // 10)
            opPos += 4
        elif opCode == 3:               # Input data from the input vector
            program[program[opPos + 1]] = inVec[inPos]
            inPos += 1
            opPos += 2
        elif opCode == 4:               # Return the output data
            return fetch(program, opPos + 1, modes % 10)
            #opPos += 2
        elif opCode == 5:               # Jump if true
            if fetch(program, opPos + 1, modes % 10) != 0: opPos = fetch(program, opPos + 2, modes % 100 // 10)
            else: opPos += 3
        elif opCode == 6:               # Jump if false
            if fetch(program, opPos + 1, modes % 10) == 0: opPos = fetch(program, opPos + 2, modes % 100 // 10)
            else: opPos += 3
        elif opCode == 7:               # Less than
            if fetch(program, opPos + 1, modes % 10) < fetch(program, opPos + 2, modes % 100 // 10):
                program[program[opPos + 3]] = 1
            else:
                program[program[opPos + 3]] = 0
            opPos += 4
        elif opCode == 8:               # Equals
            if fetch(program, opPos + 1, modes % 10) == fetch(program, opPos + 2, modes % 100 // 10):
                program[program[opPos + 3]] = 1
            else:
                program[program[opPos + 3]] = 0
            opPos += 4
        elif opCode == 99:              # Break
            print("Reached end instruction before returning any value... aborting")
            return
        else:
            print("Unknown opcode... aborting.")
            return

# Executes the program with a given input vector
def execute_pt2(program, opPos, inVec, outVec):
    # Step through program
    while True:
        opCode = program[opPos] % 100   # Extract operand
        modes = program[opPos] // 100   # Extract parameter modes

        if opCode == 1:                 # Addition
            program[program[opPos + 3]] = fetch(program, opPos + 1, modes % 10) + fetch(program, opPos + 2, modes % 100 // 10)
            opPos += 4
        elif opCode == 2:               # Multiplication
            program[program[opPos + 3]] = fetch(program, opPos + 1, modes % 10) * fetch(program, opPos + 2, modes % 100 // 10)
            opPos += 4
        elif opCode == 3:               # Input data from the input vector
            program[program[opPos + 1]] = inVec.pop(0)
            opPos += 2
        elif opCode == 4:               # Push output data to the output vector and return
            outVec.append(fetch(program, opPos + 1, modes % 10))
            opPos += 2
            return opPos
        elif opCode == 5:               # Jump if true
            if fetch(program, opPos + 1, modes % 10) != 0: opPos = fetch(program, opPos + 2, modes % 100 // 10)
            else: opPos += 3
        elif opCode == 6:               # Jump if false
            if fetch(program, opPos + 1, modes % 10) == 0: opPos = fetch(program, opPos + 2, modes % 100 // 10)
            else: opPos += 3
        elif opCode == 7:               # Less than
            if fetch(program, opPos + 1, modes % 10) < fetch(program, opPos + 2, modes % 100 // 10):
                program[program[opPos + 3]] = 1
            else:
                program[program[opPos + 3]] = 0
            opPos += 4
        elif opCode == 8:               # Equals
            if fetch(program, opPos + 1, modes % 10) == fetch(program, opPos + 2, modes % 100 // 10):
                program[program[opPos + 3]] = 1
            else:
                program[program[opPos + 3]] = 0
            opPos += 4
        elif opCode == 99:              # Break
            return -1
        else:
            print("Unknown opcode... aborting.")
            exit

#
# Process input
#
with open('day 7/input.txt') as file:
    programText = file.read().strip()

# Convert program to an array of integers
program = list(map(int, programText.split(',')))

#
# Puzzle 1
#

maxVal = 0

# Try all phase settings
for a in range(5):
    aVal = execute_pt1(program.copy(), [a, 0])
    for b in range(5):
        bVal = execute_pt1(program.copy(), [b, aVal])
        for c in range(5):
            cVal = execute_pt1(program.copy(), [c, bVal])
            for d in range(5):
                dVal = execute_pt1(program.copy(), [d, cVal])
                for e in range(5):
                    eVal = execute_pt1(program.copy(), [e, dVal])

                    # Check if no phase settings are used more than once and previous max is surpassed
                    phases = [a, b, c, d, e]
                    if len(dict.fromkeys(phases)) == 5 and eVal > maxVal:
                        maxVal = eVal
                        maxPhases = phases

print(f'Puzzle 1 solution is: {maxVal}')

#
# Puzzle 2
#
maxVal = 0

# Try all phase settings
for a in range(5):
    for b in range(5):
        for c in range(5):
            for d in range(5):
                for e in range(5):
                    # Check if no phase settings are used more than once
                    phases = [a+5, b+5, c+5, d+5, e+5]
                    if len(dict.fromkeys(phases)) == 5:
                        inVec = [[a+5, 0], [b+5], [c+5], [d+5], [e+5]]  # Initialize input vector, incl first (0) signal
                        opPoses = [0, 0, 0, 0, 0]                       # Initialize opPos vector
                        # Initialize programs for all amps
                        programs = [program.copy(), program.copy(), program.copy(), program.copy(), program.copy()]
                        while opPoses[0] >= 0:
                            for i in range(5):
                                opPoses[i] = execute_pt2(programs[i], opPoses[i], inVec[i], inVec[(i+1) % 5])
                            # Remember the input value to amp 0 (which is the same as the output value) from this iteration
                            curVal = inVec[0][0]

                        # Remember the vector if this is bigger than previous max
                        if curVal > maxVal:
                            maxVal = curVal
                            maxPhases = phases

print(f'Puzzle 2 solution is:{maxVal}')