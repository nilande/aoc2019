#
# Functions
#
def get_fuel(inputs: list):
    return list(map(lambda x: max(0, x//3 - 2), inputs))

#
# Process input
#
with open('day 1/input.txt', 'r') as file:
    modules = map(int, file.readlines())

#
# Puzzle 1
#
fuel_requirements = get_fuel(modules)
total_fuel = sum(fuel_requirements)
print(f'Puzzle 1 solution is: {total_fuel}')

#
# Puzzle 2
#
while sum(fuel_requirements) > 0:
    fuel_requirements = get_fuel(list(fuel_requirements))
    total_fuel += sum(fuel_requirements)

print(f'Puzzle 2 solution is: {total_fuel}')