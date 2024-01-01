import time, functools, math

#
# Helper functions
#

def deal_into_new_stack(deck: list) -> list:
    return deck[::-1]

def cut_cards(deck: list, cut: int) -> list:
    return deck[cut:] + deck[:cut]

def deal_with_increment(deck: list, increment: int) -> list:
    """Requires that list length and increment are coprime numbers"""
    mod = len(deck)
    mod_inv = pow(increment, -1, mod)
    return [deck[i*mod_inv % mod] for i in range(mod)]

def get_position_of(deck: list, card: int) -> int:
    return next(i for i, n in enumerate(deck) if n == card)

def get_reverse_instruction_LCFs(instructions: list, deck_size: int) -> list:
    """Compiles a set of instructions to the LCFs required to apply the instructions in reverse"""
    LCFs = []
    for instruction in instructions[::-1]:
        match instruction.split():
            case ['cut', n]:
                LCFs.append((1, int(n)))
            case ['deal', 'into', 'new', 'stack']:
                LCFs.append((-1, -1))
            case ['deal', 'with', 'increment', n]:
                LCFs.append((pow(int(n), -1, deck_size), 0))
    return LCFs

def compose_LCFs(a: tuple, b: tuple, mod: int) -> tuple:
    return (a[0]*b[0] % mod, (a[1]*b[0]+b[1]) % mod)

def iterate_LCF(LCF: tuple, iterations: int, mod: int) -> tuple:
    """Helper function that applies a LCF to itself a huge number of times"""
    LCF_stack = []
    current_LCF = LCF
    while iterations != 0:
        if iterations & 1:
            LCF_stack.append(current_LCF)
        current_LCF = compose_LCFs(current_LCF, current_LCF, mod)
        iterations >>= 1
    return functools.reduce(lambda a, b: compose_LCFs(a, b, mod), LCF_stack[::-1])

#
# Process input
#
with open('day 22/input.txt') as file:
    instructions = file.read().splitlines()

#
# Puzzle 1
#
deck = list(range(10007))

for instruction in instructions:
    match instruction.split():
        case ['cut', n]:
            deck = cut_cards(deck, int(n))
        case ['deal', 'into', 'new', 'stack']:
            deck = deal_into_new_stack(deck)
        case ['deal', 'with', 'increment', n]:
            deck = deal_with_increment(deck, int(n))
        
print(f'Puzzle 1 solution is: {get_position_of(deck, 2019)}')

#
# Puzzle 2
#
deck_size = 119315717514047
target_pos = 2020
num_shuffles = 101741582076661

# Get the list of LCFs required to transform the shuffle in reverse once
instruction_LCFs = get_reverse_instruction_LCFs(instructions, deck_size)

# Compose the list of LCFs into one LCF that performs the shuffle in one go
one_shuffle_LCF = functools.reduce(lambda a, b: compose_LCFs(a, b, deck_size), instruction_LCFs)

# Compose the huge number of shuffles into one mega-shuffle
mega_shuffle_LCF = iterate_LCF(one_shuffle_LCF, num_shuffles, deck_size)

print(f'Puzzle 2 solution is: {(mega_shuffle_LCF[0]*target_pos + mega_shuffle_LCF[1]) % deck_size}')