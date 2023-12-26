#
# Process input
#
with open('day 4/input.txt') as file:
    content = file.read().strip()
numbers = list(map(int, content.split('-')))

#
# Puzzle 1
#
def test1(num):
    dig = num % 10                          # Least significant digit
    num = num // 10                         # Remaining (more significant) digits
    double = False                          # Variable to identify if double has been found
    while (num > 0):
        nextDig = num % 10                    # Next least significant digit
        if nextDig > dig: return False        # Failed due to less significant digit decreasing
        elif nextDig == dig: double = True    # Two adjacent figures are the same
        else: dig = nextDig                   # Update least significant digit
        num = num // 10
    return double

counter=0

for num in range(numbers[0], numbers[1]):
    if test1(num): counter += 1

print(f'Puzzle 1 solution is: {counter}')

#
# Puzzle 2
#
def test2(num):
  dig = num % 10                          # Least significant digit
  num = num // 10                         # Remaining (more significant) digits
  double = False                          # Variable to identify if double has been found
  streak = 1                              # Counter of repeating streaks of the same digit
  while (num > 0):
    nextDig = num % 10                    # Next least significant digit
    if nextDig > dig: return False        # Failed due to less significant digit decreasing
    elif nextDig == dig: streak += 1      # Two adjacent figures are the same, increment the streak counter
    else:                                 # Least significant digit is changing
      if streak == 2: double = True       # A double has been found
      streak = 1                          # Reset the streak counter to 1
      dig = nextDig                       # Update least significant digit
    num = num // 10
  if streak == 2: double = True           # A double has been found in the end
  return double

counter=0

for num in range(numbers[0], numbers[1]):
  if test2(num): counter += 1

print(f'Puzzle 2 solution is: {counter}')