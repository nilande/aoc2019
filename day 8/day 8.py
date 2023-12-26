#
# Functions
#
def wrap(text: str, width: int):
    wrapped = []
    while len(text) > 0:
        wrapped.append(text[:width])
        text = text[width:]
    return wrapped

#
# Process input
#
with open('day 8/input.txt') as file:
    inputText = file.read().strip()

#
# Puzzle 1
#
imageW = 25
imageH = 6

layers = wrap(inputText, imageW * imageH)
layersDict = []

# Initialize min zeros to something big...
minZeros = 1E10

for layer in layers:
    dict = {'0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0 }
    for char in layer:
        dict[char] += 1
    layersDict.append(dict)
    if dict['0'] < minZeros:
        minZeros = dict['0']
        minValue = dict['1'] * dict['2']

print(f'Puzzle 1 solution is: {minValue}')

#
# Puzzle 2
#
flattened = ['2'] * imageW * imageH

# Go through each pixel
for i in range(imageW * imageH):
    layer = 0
    while flattened[i] == '2':
        flattened[i] = layers[layer][i]
        layer += 1

# Replace codes with pixels
flattened = ['OO' if x == '1' else '  ' for x in flattened]

# Merge to string and split into rows
rows = wrap("".join(flattened), imageW*2)

print(f'Puzzle 2 solution is:')
for row in rows: print(row)