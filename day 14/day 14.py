#
# Classes
#
class Reaction:
    """This class has the functions to keep track of production recipes and quantities"""
    def __init__(self, init_str: str) -> None:
        ingredients_str, result_str = init_str.split(' => ')
        q, self.name = result_str.split()
        self.batch_size = int(q)
        self.ingredients = {}
        for iq, ingredient_name in map(lambda x: x.split(), ingredients_str.split(', ')):
            self.ingredients[ingredient_name] = int(iq)
        self.reset_quantities()

    def reset_quantities(self) -> None:
        self.quantity_produced = 0
        self.quantity_available = 0

    def load_reactions(self, reactions: dict):
        self.reactions = reactions

    def produce(self, quantity_ordered: int) -> None:
        quantity_needed = quantity_ordered - self.quantity_available
        if quantity_needed > 0:
            batch_count = -(quantity_needed // -self.batch_size)
            for r, q in self.ingredients.items(): self.reactions[r].produce(q * batch_count)
            batch_quantity_produced = batch_count * self.batch_size
            self.quantity_available += batch_quantity_produced
            self.quantity_produced += batch_quantity_produced
        self.quantity_available -= quantity_ordered

class Ore(Reaction):
    """Special class to keep track of ORE production, which is not a separate recipe"""
    def __init__(self) -> None:
        self.reset_quantities()

    def produce(self, quantity_ordered: int) -> None:
        self.quantity_produced += quantity_ordered

#
# Functions
#
def get_ore_from_fuel(reactions: dict, fuel: int) -> int:
    """Calculates the ORE required to produce a certain amount of FUEL"""
    for r in reactions.values(): r.reset_quantities()
    reactions['FUEL'].produce(fuel)
    return reactions['ORE'].quantity_produced

#
# Process input
#
with open('day 14/input.txt') as file:
    reactions = {r.name: r for r in map(lambda x: Reaction(x), file.read().splitlines())}
for r in reactions.values(): r.load_reactions(reactions)
reactions['ORE'] = Ore()

#
# Puzzle 1
#
reactions['FUEL'].produce(1)

print(f'Puzzle 1 solution is: {reactions["ORE"].quantity_produced}')

#
# Puzzle 2
#
target_value = 1000000000000
tested_fuels = set()

# Initial test
last_fuel, last_ore = (1, get_ore_from_fuel(reactions, 1))

while last_fuel not in tested_fuels:
    # Calculate the next value to test with
    next_fuel = target_value * last_fuel // last_ore

    # Add the previously tested value to the set of tested values
    tested_fuels.add(last_fuel)

    # Conduct a new test
    last_fuel, last_ore = (next_fuel, get_ore_from_fuel(reactions, next_fuel))

print(f'Puzzle 2 solution is: {last_fuel}')