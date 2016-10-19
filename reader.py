import os
import fileinput

PREFIX = './data'
EXT = '.data'

def process(line):
    l, v = line.split()
    return (l, v)

def read_files(input_file):
    files = [
            os.path.join(PREFIX, input_file, input_file + '_' + str(i) + EXT)
            for i in range(4)]

    instructions = [[],[],[],[]]
    for i, afile in enumerate(files):
        with open(afile) as f:
            for line in f:
                instructions[i].append(process(line))
    print(len(instructions[0]))
