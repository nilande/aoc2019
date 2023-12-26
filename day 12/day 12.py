import copy, functools, math, time

#
# Classes
#
class Moon:
    def __init__(self, init_string: str) -> None:
        self.P = tuple(map(lambda x: int(x.split('=')[1]), init_string[1:-1].split(', ')))
        self.V = (0, 0, 0)

    def __repr__(self) -> str:
        return f'P={self.P}, V={self.V}'

    def load_moons(self, moons: list) -> None:
        self.moons = moons

    def apply_gravity(self) -> None:
        for other in self.moons:
            if other == self: continue
            G = tuple((p1 < p2) - (p1 > p2)  for p1, p2 in zip(self.P, other.P))
            self.V = tuple(sum(x) for x in zip(self.V, G))

    def apply_velocity(self) -> None:
        self.P = tuple(sum(x) for x in zip(self.P, self.V))

    def get_energy(self) -> int:
        return sum(abs(x) for x in self.P) * sum(abs(x) for x in self.V)


#
# Process input
#
with open('day 12/input.txt') as file:
    moons = list(map(lambda x: Moon(x), file.read().splitlines()))
for moon in moons: moon.load_moons(moons)
moons_copy = copy.deepcopy(moons)

#
# Puzzle 1
#
for i in range(1000):
    for moon in moons: moon.apply_gravity()
    for moon in moons: moon.apply_velocity()

total_energy = 0
for moon in moons: total_energy += moon.get_energy()

print(f'Puzzle 1 solution is: {total_energy}')

#
# Puzzle 2
#
moons = moons_copy
start_time = time.time()

# Save initial state for comparison
initial_state = [None] * 3
current_state = [None] * 3
first_recurrence = [None] * 3
for i in range(3): initial_state[i] = [ moon.P[i] for moon in moons ] + [ moon.V[i] for moon in moons ]

i = 0
while any(x == None for x in first_recurrence):
    for moon in moons: moon.apply_gravity()
    for moon in moons: moon.apply_velocity()
    i += 1

    # Compare dimensions to initial state and save first recurrence of each dimension
    for j in range(3):
        if not first_recurrence[j] is None: continue
        current_state[j] = [ moon.P[j] for moon in moons ] + [ moon.V[j] for moon in moons ]
        if initial_state[j] == current_state[j]: first_recurrence[j] = i

# Result is least common multiple of each dimension
first_recurrence = functools.reduce(math.lcm, first_recurrence)
print(f'Puzzle 2 solution is: {first_recurrence} (in {time.time() - start_time:.3f} seconds)')
