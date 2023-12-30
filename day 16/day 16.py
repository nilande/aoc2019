import numpy as np

#
# Process input
#
with open('day 16/input.txt') as file:
    input_signal = np.array([int(c) for c in file.read().strip()])

#
# Puzzle 1
#

# Prepare multiplication matrix
length = len(input_signal)
base_pattern = np.array([0, 1, 0, -1])
pattern_matrix = np.zeros((length, length), dtype=int)
for i in range(length):
    pattern_matrix[i, :] = np.tile(np.repeat(base_pattern, i+1), -((length+i+1) // -(4 * (i+1))))[1:length+1]

phase_output_signal = input_signal

# Run the matrix multiplication 100 times
for i in range(100):
    phase_output_signal = np.array([abs(x)%10 for x in np.matmul(pattern_matrix, phase_output_signal)])

print(f'Puzzle 1 solution is: {''.join(map(str, phase_output_signal[:8]))}')

#
# Puzzle 2
#
offset = int(''.join(map(str, input_signal[:7])))
trunc_signal = np.tile(input_signal, 10000)[offset:]
length = len(trunc_signal)

# Due to offset being in 2nd half, each phase transformation is essentially a running total from the end
for i in range(100):
    acc = trunc_signal[-1]
    for j in range(length-2, -1, -1):
        acc = (acc + trunc_signal[j]) % 10
        trunc_signal[j] = acc

print(f'Puzzle 2 solution is: {''.join(map(str, trunc_signal[:8]))}')