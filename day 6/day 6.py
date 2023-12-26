#
# Process input
#
with open('day 6/input.txt') as file:
    puzzleInput = file.read().splitlines()

#
# Puzzle 1
#
    
# Create a dictionary containing parents for a given child (only one child per parent)
parents = {}
for orbit in puzzleInput:
    parent, child = orbit.split(')')
    parents[child] = parent

# Count orbits for a given object
def countOrbits(obj):
    count = 0
    if obj in parents: count = 1 + countOrbits(parents[obj])
    return count

# Count total orbits
total = 0
for obj in parents:
    total += countOrbits(obj)

print(f'Puzzle 1 solution is: {total}')

#
# Puzzle 2
#

# Get list of parents for a given object
def getParentList(obj):
    parentList = []
    if obj in parents: parentList = [parents[obj]] + getParentList(parents[obj])
    return parentList

# Get the list of parents from your orbit and Santa's
youPath = getParentList('YOU')
sanPath = getParentList('SAN')

# Remove all common orbit parents as they are not needed for the transfer
while youPath[-1] == sanPath[-1]:
    youPath.pop()
    sanPath.pop()

# The combined length of resulting vectors is the result
print(f'Puzzle 2 solution is: {len(youPath) + len(sanPath)}')