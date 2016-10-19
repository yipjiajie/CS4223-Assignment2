from math import log

def log2(x): return int(log(x, 2))

class ReadMiss(Exception):
    pass

class WriteMiss(Exception):
    pass

class CacheLine():
    def __init__(self):
        self.valid = False
        self.dirty = False
        self.tag = None
        self.data = []

class Cache():
    def __init__(self, cache_size, assoc, block_size):
        self.cache_size = cache_size # number of bytes
        self.assoc = assoc
        self.block_size = block_size # number of bytes
        self.word_size = 4 # fixed

        self.n_words_in_block = self.block_size / self.word_size
        self.n_blocks = self.cache_size / self.block_size

        self.n_bits_offset = log2(self.block_size)
        self.n_bits_index = log2(self.n_blocks)
        self.n_bits_tag = 32 - self.n_bits_offset - self.n_bits_index

        self.offset_mask = int(pow(2, self.n_bits_offset)) - 1
        self.index_mask = int(pow(2, self.n_bits_index)) - 1

        self._cache = [
            CacheLine() for i in range(self.n_blocks)
            ]

    def offset(self, mem_addr):
        return mem_addr & self.offset_mask

    def index(self, mem_addr):
        return (mem_addr >> self.n_bits_offset) & self.index_mask

    def tag(self, mem_addr):
        return mem_addr >> (self.n_bits_offset + self.n_bits_index)

    def cache_line(self, mem_addr):
        return self._cache[self.index(mem_addr)]

    def read(self, mem_addr):
        cache_line = self.cache_line(mem_addr)
        if cache_line.valid:
            if cache_line.tag == self.tag(mem_addr):
                # cache hit
                return None
            else:
                # tag mismatch
                # need to load and update tag
                # check dirty bit and write
                raise ReadMiss('tag mismatch')
        else:
            # cold miss
            # need to load and set valid and tag
            raise ReadMiss('cache line invalid')

    def write(self, mem_addr):
        cache_line = self.cache_line(mem_addr)
        if cache_line.valid:
            if cache_line.tag == self.tag(mem_addr):
                # can write to offset
                cache_line.dirty = True
                return None
            else:
                # write-allocate
                raise WriteMiss('tag mismatch')
        else:
            # write-allocate
            raise WriteMiss('cache line invalid')
