#
# Functions
#

# positions have thee elements: x, y and distance. Distance is only needed for part #2 of this exercise

def goUp(pos, steps):
    pos[1] += steps
    pos[2] += steps # Increment path distance element, needed for part B

def goDown(pos, steps):
    pos[1] -= steps
    pos[2] += steps # Increment path distance element, needed for part B

def goRight(pos, steps):
    pos[0] += steps
    pos[2] += steps # Increment path distance element, needed for part B

def goLeft(pos, steps):
    pos[0] -= steps
    pos[2] += steps # Increment path distance element, needed for part B

# Switch statement corresponding to above functions
goDirection = {
    "U": goUp,
    "D": goDown,
    "R": goRight,
    "L": goLeft
}

def goStep(pos, vecStep):
    # Split vector step (e.g. R142) into direction (R) and steps (142)
    direction, steps = vecStep[:1], int(vecStep[1:])
    # Execute stepping function (switch statement)
    goDirection.get(direction)(pos, steps)


#
# Process input
#
with open('day 3/input.txt') as file:
    input = file.readlines()
inputA = input[0]
inputB = input[1]

#
# Puzzle 1
#
def compareTC(a1, a2, b1, b2):
  # Test if a is vertical, b is horisontal
  if (a1[0]==a2[0]) and (b1[1]==b2[1]):
    # Test if b crosses a horisontally
    if (b1[0] < a1[0] < b2[0]) or (b1[0] > a1[0] > b2[0]):
      # Test if a crosses b vertically
      if (a1[1] < b1[1] < a2[1]) or (a1[1] > b1[1] > a2[1]):
        # We have a cross! Return taxicab distance
        return abs(a1[0])+abs(b1[1])

  # Test if a is horisontal, b is vertical
  if (a1[1]==a2[1]) and (b1[0]==b2[0]):
    # Test if a crosses b horisontally
    if (a1[0] < b1[0] < a2[0]) or (a1[0] > b1[0] > a2[0]):
      # Test if b crosses a vertically
      if (b1[1] < a1[1] < b2[1]) or (b1[1] > a1[1] > b2[1]):
        # We have a cross! Return taxicab distance
        return abs(b1[0])+abs(a1[1])

# Initialize inputs
#inputA = "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51"
#inputB = "U98,R91,D20,R16,D67,R40,U7,R15,U6,R7"

# Split into vectors
vecA = inputA.split(',')
vecB = inputB.split(',')

# Start with an empty list of taxicab distances
distances = []

# Initialize vector A position and step through vector A
aPos = [0, 0, 0]
for a in range(len(vecA)):
  aPosOld = aPos.copy()
  goStep(aPos, vecA[a])
  
  # Initialize vector B position and step through vector B
  bPos = [0, 0, 0]
  for b in range(len(vecB)):
    bPosOld = bPos.copy()
    goStep(bPos, vecB[b])

    result = compareTC(aPos, aPosOld, bPos, bPosOld)
    if result: distances.append(result)

print(f'Puzzle 1 solution is: {min(distances)}')

#
# Puzzle 2
#
# Compare vectors and return number of steps taken if the wires cross
def compareNS(a1, a2, b1, b2):
  # Test if a is vertical, b is horisontal
  if (a1[0]==a2[0]) and (b1[1]==b2[1]):
    # Test if b crosses a horisontally
    if (b1[0] < a1[0] < b2[0]) or (b1[0] > a1[0] > b2[0]):
      # Test if a crosses b vertically
      if (a1[1] < b1[1] < a2[1]) or (a1[1] > b1[1] > a2[1]):
        # We have a cross! Return path distances for wires A and B
        return [a2[2]+abs(b2[1]-a2[1]), b2[2]+abs(b2[0]-a2[0])]

  # Test if a is horisontal, b is vertical
  if (a1[1]==a2[1]) and (b1[0]==b2[0]):
    # Test if a crosses b horisontally
    if (a1[0] < b1[0] < a2[0]) or (a1[0] > b1[0] > a2[0]):
      # Test if b crosses a vertically
      if (b1[1] < a1[1] < b2[1]) or (b1[1] > a1[1] > b2[1]):
        # We have a cross! Return path distances for wires A and B
        return [a2[2]+abs(b2[0]-a2[0]), b2[2]+abs(b2[1]-a2[1])]

# Find all path lengths where wires A and B cross
def findCrosses(inputA, inputB):
  # Split into vectors
  vecA = inputA.split(',')
  vecB = inputB.split(',')

  # Initialize return vector
  resultArray = []

  # Initialize vector A position and step through vector A
  aPos = [0, 0, 0]
  for a in range(len(vecA)):
    aPosOld = aPos.copy()
    goStep(aPos, vecA[a])
    
    # Initialize vector B position and step through vector B
    bPos = [0, 0, 0]
    for b in range(len(vecB)):
      bPosOld = bPos.copy()
      goStep(bPos, vecB[b])

      result = compareNS(aPos, aPosOld, bPos, bPosOld)
      if result: resultArray.append(result)
  
  # Return the array of vector lengths where the wires cross
  return resultArray

# Sort cross path lengths and remove duplicates (only used when testing a wire against itself)
def sortCrosses(pLens):
  # Swap positions so that first is always smallest
  for pLen in pLens:
    if pLen[0]>pLen[1]:
      pLen[0], pLen[1] = pLen[1], pLen[0]
  
  pLens = sorted(pLens, key=lambda x: x[0])
  # Return every second element (since the rest should be duplicates)
  return pLens[0::2]

# Find distances where A crosses B amd sort by path length
AxB = findCrosses(inputA, inputB)
AxB = sorted(AxB, key=lambda x: x[0]+x[1])

print(f'Puzzle 2 solution is: {AxB[0][0] + AxB[0][1]}')