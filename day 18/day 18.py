import functools
from heapq import heappush, heappop
from collections import deque

#
# Classes
#
class VaultObject:
    ENTRANCE = 0
    KEY = 1
    DOOR = 2

    def __init__(self, name: str, pos: complex) -> None:
        self.name = name
        self.pos = pos

        if name.isupper():
            self.type = VaultObject.DOOR
            self.key_mask = 1 << ord(name) - ord('A')
            self.inverse_key_mask = ~self.key_mask
        elif name.islower():
            self.type = VaultObject.KEY
            self.key_mask = 1 << ord(name) - ord('a')
            self.inverse_key_mask = ~self.key_mask
        else:
            self.type = VaultObject.ENTRANCE
            self.key_mask = 0


    def __repr__(self) -> str:
        return f"{self.name}*"
    
    def add_neighbors(self, neighbors: dict):
        self.neighbors = neighbors

    def find_path_to_other_keys(self):
        id = 0 
        # Queue contains tuples with the following structure:
        # (path length in steps, unique heap id, object to explore, mask of keys required to reach this point, path to get here)
        queue = [ (0, id, self, 0, []) ]

        # Explored is a dictionary, containing what objects have been explored with a given set of keys
        # (i.e. the key is the tuple of keys in alphabetical order, the value is the objects that have been explored)
        explored = {0: set()}
        
        # other_keys is a dictionary, containing the list of other keys that have been found
        # (the key is the mask of keys required to make the journey)
        path_to_other_keys = {0: {}}

        while len(queue) > 0:
            steps, _, obj, keys_mask, path = heappop(queue)

            # Make sure we are not exploring paths that have been explored with a subset of our keys
            has_been_explored = False
            for k in explored:
                if keys_mask == keys_mask | k and obj in explored[k]:
                    has_been_explored = True
                    break
            if has_been_explored: continue

            explored[keys_mask].add(obj)
            path.append(obj)
            if obj.type == VaultObject.KEY and obj != self:
                # When encountering a key, we add the result to the list of results
                path_to_other_keys[keys_mask][obj] = (steps, path)
            elif obj.type == VaultObject.DOOR:
                # When encountering a door, we create a new keylist and continue
                keys_mask |= obj.key_mask
                if not keys_mask in explored:
                    explored[keys_mask] = set()
                    path_to_other_keys[keys_mask] = {}
            for neighbor in obj.neighbors:
                id += 1
                heappush(queue, (steps + obj.neighbors[neighbor][0], id, neighbor, keys_mask, path.copy()))

        # Remove key sets that don't include any paths
        self.path_to_other_keys = {a: b for a, b in path_to_other_keys.items() if len(b) > 0}

        # print(f'Paths from {self}: {self.path_to_other_keys}')

class VaultMap:
    def __init__(self, map_string: str) -> None:
        self.traversable = set()
        self.objects = {}
        self.all_key_masks = 0

        width = map_string.find('\n') + 1
        for i in range(len(map_string)):
            pos = i%width + i//width*1j
            if map_string[i] not in {'#', '\n'}:
                self.traversable.add(pos)
                if map_string[i] != '.': self.objects[pos] = VaultObject(map_string[i], pos)
        
        for obj in self.objects.values(): self.update_neighbors_for(obj)
        for obj in self.objects.values():
            if obj.type != VaultObject.DOOR: obj.find_path_to_other_keys()
            if obj.type == VaultObject.KEY: self.all_key_masks |= obj.key_mask

    def update_neighbors_for(self, obj: VaultObject) -> None:
        """Determine the neighbor objects to this object and inform this one about its neighbors"""
        queue = deque([ (obj.pos, set()) ])
        explored = set()
        neighbors = {}

        while len(queue) > 0:
            pos, path = queue.popleft()
            if pos in explored: continue
            explored.add(pos)
            path.add(pos)
            if len(path) > 1 and pos in self.objects and self.objects[pos].type != VaultObject.ENTRANCE:
                neighbors[self.objects[pos]] = (len(path)-1, path)
            else:
                next_pos = { pos+1, pos-1, pos+1j, pos-1j } & self.traversable
                for np in next_pos: queue.append((np, path.copy()))

        obj.add_neighbors(neighbors)

#
# Helper functions
#
def mask_to_char(mask: int) -> chr:
    if mask == 0: return '@'

    char = 96
    while mask != 0:
        mask >>= 1
        char += 1

    return chr(char)

#
# Main function
#
if __name__ == "__main__":

    #
    # Puzzle 1
    #
    with open('day 18/input.txt') as file:
        vault_map = VaultMap(file.read())

    # Build a travel dictionary like this:
    # travel_dict[from_mask][to_mask] = (steps, keys_required_mask)
    travel_dict = {}
    objs = [o for o in vault_map.objects.values() if o.type != VaultObject.DOOR]
    for fr in objs:
        for km, other in fr.path_to_other_keys.items():
            for to, steps in other.items():
                travel_dict.setdefault(fr.key_mask, {})
                travel_dict[fr.key_mask][to.key_mask] = (steps[0], km)

    @functools.cache
    def find_shortest_path_length(this_keymask: int, remaining_keymask: int) -> tuple:
        # End if we have no remaining places to visit
        if remaining_keymask == 0: return (0, '')

        # Loop through next places to visit
        next_keymask = 1
        temp_mask = remaining_keymask
        fewest_steps = None
        while temp_mask != 0:
            if next_keymask & temp_mask != 0:
                temp_mask -= next_keymask

                # Let's try if it is possible to go from this_keymask to next_keymask
                next_steps, keys_required_mask = travel_dict[this_keymask][next_keymask]

                # Only if there is no overlap between keys required and keys remaining, we can make the journey
                if remaining_keymask & keys_required_mask == 0:
                    remaining_steps, remaining_sequence = find_shortest_path_length(next_keymask, remaining_keymask & ~next_keymask)
                    total_steps = next_steps + remaining_steps
                    if fewest_steps is None or total_steps < fewest_steps:
                        fewest_steps = total_steps
                        fewest_steps_sequence = mask_to_char(next_keymask) + remaining_sequence

            next_keymask <<= 1

        return fewest_steps, fewest_steps_sequence 

    fewest_steps, fewest_steps_sequence = find_shortest_path_length(0, vault_map.all_key_masks)

    print(f'Puzzle 1 solution is: {fewest_steps} (key sequence is {fewest_steps_sequence})')

    #
    # Puzzle 2
    #
    with open('day 18/input_mod.txt') as file:
        vault_map = VaultMap(file.read())

    # Build a travel dictionary like this:
    # travel_dict[from_mask][to_mask] = (steps, keys_required_mask)
    entrance_no = 0
    travel_dict = {}
    objs = [o for o in vault_map.objects.values() if o.type != VaultObject.DOOR]
    for fr in objs:
        if fr.type == VaultObject.ENTRANCE:
            entrance_no -= 1
            travel_dict.setdefault(entrance_no, {})
        for km, other in fr.path_to_other_keys.items():
            for to, steps in other.items():
                if fr.type == VaultObject.ENTRANCE:
                    travel_dict[entrance_no][to.key_mask] = (steps[0], km)
                else:
                    travel_dict.setdefault(fr.key_mask, {})
                    travel_dict[fr.key_mask][to.key_mask] = (steps[0], km)

    @functools.cache
    def find_shortest_multipath_length(these_keymasks: tuple, remaining_keymask: int) -> tuple:
        # End if we have no remaining places to visit
        if remaining_keymask == 0: return (0, '')

        # Loop through next places to visit
        next_keymask = 1
        temp_mask = remaining_keymask
        fewest_steps = None
        while temp_mask != 0:
            if next_keymask & temp_mask != 0:
                temp_mask -= next_keymask

                # Figure out which of the bots can travel to the target
                for i in range(4):
                    if these_keymasks[i] in travel_dict and next_keymask in travel_dict[these_keymasks[i]]:
                        # Potential path found
                        next_steps, keys_required_mask = travel_dict[these_keymasks[i]][next_keymask]
                        next_keymasks = list(these_keymasks)
                        next_keymasks[i] = next_keymask
                        break

                # Only if there is no overlap between keys required and keys remaining, we can make the journey
                if remaining_keymask & keys_required_mask == 0:
                    remaining_steps, remaining_sequence = find_shortest_multipath_length(tuple(next_keymasks), remaining_keymask & ~next_keymask)
                    total_steps = next_steps + remaining_steps
                    if fewest_steps is None or total_steps < fewest_steps:
                        fewest_steps = total_steps
                        fewest_steps_sequence = mask_to_char(next_keymask) + remaining_sequence

            next_keymask <<= 1

        return fewest_steps, fewest_steps_sequence
    
    fewest_steps, fewest_steps_sequence = find_shortest_multipath_length((-1, -2, -3, -4), vault_map.all_key_masks)

    print(f'Puzzle 2 solution is: {fewest_steps} (key sequence is {fewest_steps_sequence})')