import os
import fileinput

PREFIX = './data'
EXT = '.data'

def process(line):
    l, v = line.split()
    return (l, v)

def read_instruction(input_file, processor_number):
    filename = ''.join([input_file, '_', str(processor_number), EXT])
    filepath = os.path.join(PREFIX, input_file, filename)

    instructions = []
    with open(filepath) as f:
        instructions = [line.strip() for line in f]
    return instructions
