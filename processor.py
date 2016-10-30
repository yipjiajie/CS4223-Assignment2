from reader import read_instruction

class Processor():
    def __init__(self, input_file, pn, cache):
        self.pn = pn
        self.instructions = read_instruction(input_file, pn)
        self.cycle = 0
        self.ic = 0
        self.cache = cache
        # cycles remaining for computation
        self.compute_for_cycles = 0
        # cycles remaming for some memory operation
        self.memory_access_cycles = 0

    def tick(self):
        if self.cache.is_blocked():
            self.cycle += 1
            return

        elif self.compute_for_cycles > 0:
            self.compute_for_cycles -= 1
            self.cycle += 1
            return

        elif self.ic >= len(self.instructions):
            return True

        instr = self.instructions[self.ic]
        ty, mem = instr.split()

        self.ic += 1
        return (self.ic-1, ty, mem)

    def compute_for(self, cycles):
        self.compute_for_cycles += cycles

    def get_summary(self):
        return {
            'cycles': self.cycle,
        }
