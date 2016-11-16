from reader import read_instruction

class Processor():
    def __init__(self, input_file, pn, cache):
        self.pn = pn
        self.instructions = read_instruction(input_file, pn)
        self.cycle = 0
        self.ic = 0
        self.cache = cache
        self.cache.processor = self
        # cycles remaining for computation
        self.compute_for_cycles = 0
        # cycles remaming for some memory operation
        self.memory_access_cycles = 0
        self.total_compute = 0
        self.num_cycles = len(self.instructions)
        self.done = False

    def tick(self):
        if self.done:
            return

        if self.compute_for_cycles > 0:
            self.compute_for_cycles -= 1
            self.cycle += 1
            return

        if self.cache._blocked_for > 0:
            self.cycle += 1
            return

        if self.ic >= self.num_cycles:
            self.done = True
            return True

        instr = self.instructions[self.ic]
        ty = instr[0:1]
        mem = instr[2:]

        return (self.ic, ty, mem)

    def proceed(self):
        if self.compute_for_cycles == 0:
            self.ic += 1
            # if self.ic % 10000 == 0:
            #     print('proceeding %s %s' % (self.pn, self.ic))

    def compute_for(self, cycles):
        self.total_compute += cycles
        self.compute_for_cycles += cycles

    def get_summary(self):
        return {
            'cycles': self.cycle,
            'total_compute': self.total_compute,
        }
