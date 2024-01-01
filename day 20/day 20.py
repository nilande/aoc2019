from collections import deque

#
# Classes
#
class PlutoMap:
    def __init__(self, map_string: str) -> None:
        width = map_string.find('\n') + 1
        height = -(len(map_string) // -width)
        self.walkable = set()

        # Identify walkable tiles
        for i, c in enumerate(map_string):
            match c:
                case '.': self.walkable.add(i)

        # Search for neighbors and portals
        self.neighbors = {}
        portals = {}
        for i in self.walkable:
            self.neighbors[i] = {(x, 0) for x in {i-1, i+1, i-width, i+width} & self.walkable}
            portal_checks = [(i-2, i-1), (i+1, i+2), (i-2*width, i-width), (i+width, i+2*width)]
            for pa, pb in portal_checks:
                if map_string[pa].isupper() and map_string[pb].isupper():
                    portal_name = map_string[pa]+map_string[pb]
                    portals.setdefault(portal_name, [])
                    portals[portal_name].append(i)

        self.start = portals['AA'][0]
        self.finish = portals['ZZ'][0]

        # Finally, add portals to sets of neighbors
        for a, b in [x for x in portals.values() if len(x) > 1]:
            if 3 < a % width < width - 5 and 3 < a // width < height-4:
                self.neighbors[a].add((b, 1))   # a is an inner portal, leads to one level above
                self.neighbors[b].add((a, -1))  # consequently b is an outer portal, leads to one level below
            else:
                self.neighbors[a].add((b, -1))
                self.neighbors[b].add((a, 1))

#
# Process input
#
with open('day 20/input.txt') as file:
    pluto_map = PlutoMap(file.read())

#
# Puzzle 1
#
queue = deque([ (pluto_map.start, 0) ])
explored = set()

while len(queue) > 0:
    pos, steps = queue.popleft()
    if pos in explored: continue
    if pos == pluto_map.finish: break
    explored.add(pos)
    for next_pos, _ in pluto_map.neighbors[pos]:
        queue.append((next_pos, steps+1))

print(f'Puzzle 1 solution is: {steps:6} \t({len(explored):,} tiles explored in BFS)')

#
# Puzzle 2
#
queue = deque([ (pluto_map.start, 0, 0) ])
explored = set()

while len(queue) > 0:
    pos, level, steps = queue.popleft()
    if level < 0: continue # Not allowed to travel to negative levels
    if (pos, level) in explored: continue
    if pos == pluto_map.finish and level == 0: break
    explored.add((pos, level))
    for next_pos, next_level in pluto_map.neighbors[pos]:
        queue.append((next_pos, level + next_level, steps+1))

print(f'Puzzle 2 solution is: {steps:6} \t({len(explored):,} tiles explored in 3D-BFS)')