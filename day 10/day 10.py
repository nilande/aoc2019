import math

#
# Process input
#
with open('day 10/input.txt') as file:
    inputText = file.read()

#
# Puzzle 1
#
def angle(p1, p2):
    return (math.degrees(math.atan2(p2[0]-p1[0], -p2[1]+p1[1])) + 360) % 360

# List of asteroids
asteroids = []

# Translate map to a list of x, y coordinates
for y, row in enumerate(inputText.split('\n')):
    for x, char in enumerate(row):
        if char == '#':
            # We have an asteroid at (x, y)
            asteroids.append((x, y))

maxAngles = 0

# Loop through all asteroids
for a1 in asteroids:
    # Create a dictionary of angles between this asteroid and others
    angles = {}

    # Match this asteroid against all other asteroids
    for a2 in asteroids:
        # Do not check an asteroid against itself
        if a1 != a2:
            angles[angle(a1, a2)] = True

    # The number of unique angles is what we're trying to optimize here
    if len(angles) > maxAngles:
        maxAngles = len(angles)
        station = a1

print(f'Puzzle 1 solution is: {maxAngles}')

#
# Puzzle 2
#
def distance(p1, p2):
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

# Remove the station from the list of asteroids
if station in asteroids: asteroids.remove(station)

# Again, create a dictionary of angles to asteroids
angles = {}
for a in asteroids:
    sAngle = angle(station, a)
    sDistance = distance(station, a)

    if sAngle in angles:
        angles[sAngle].append((a[0], a[1], sDistance))
    else:
        angles[sAngle] = [ (a[0], a[1], sDistance) ]

# Sort the dictionary by distances
for a in angles:
    angles[a].sort(key = lambda x: x[2])

counter = 1

# Loop the laser while there are astroids to zap
while len(angles) > 0:
    for a in sorted(angles):
        zapped = angles[a].pop(0)                   # The zapped asteroid
        if len(angles[a]) == 0: del angles[a]       # Remove angles for which no asteroids are left
        if counter == 200: print(f'Puzzle 2 solution is: {zapped[0]*100 + zapped[1]}')
        counter += 1