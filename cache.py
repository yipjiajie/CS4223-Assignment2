from math import log
from msi_cache_block import CacheBlock
from debug import debug_cache

def log2(x): return int(log(x, 2))

class Cache():
    def __init__(self, cache_size, assoc, block_size, pn):
        self.id = pn
        self.cache_size = cache_size # number of bytes
        self.assoc = assoc
        self.block_size = block_size # number of bytes
        self.word_size = 4 # fixed

        self.n_words_in_block = self.block_size // self.word_size
        self.n_blocks = self.cache_size // self.block_size

        self.n_bits_offset = log2(self.block_size)
        self.n_bits_index = log2(self.n_blocks)
        self.n_bits_tag = 32 - self.n_bits_offset - self.n_bits_index

        self.offset_mask = int(pow(2, self.n_bits_offset)) - 1
        self.index_mask = int(pow(2, self.n_bits_index)) - 1

        self._cache = self.init_cache_blocks(self.id)
        self._blocked_for = 0

    def init_cache_blocks(self):
        return []

    def offset(self, mem_addr):
        return mem_addr & self.offset_mask

    def index(self, mem_addr):
        return (mem_addr >> self.n_bits_offset) & self.index_mask

    def tag(self, mem_addr):
        return mem_addr >> (self.n_bits_offset + self.n_bits_index)

    def cache_block(self, mem_addr):
        """Get cache bock responsible for this memory address"""
        return self._cache[self.index(mem_addr)]

    def tick(self):
        if self._blocked_for > 0:
            self._blocked_for -= 1

    def is_blocked(self):
        return self._blocked_for > 0

    def block_for(self, cycles):
        self._blocked_for += cycles
        debug_cache(self.id, cycles, self._blocked_for)

    def processor_action(self, event, mem_addr):
        """Respond to a processor action.

        Returns bus_txn:
            the name of bus event triggered
        """
        cache_block = self.cache_block(mem_addr)
        return cache_block.processor_action(event)

    def bus_action(self, event, mem_addr, origin):
        """Respond to a bus snoop action

        Returns (snoop, cycles to block):
            snoop is a boolean indicating if the cache block snooped this event
            cycles to block indicates cycles that the cache controll is blocked
        """
        cache_block = self.cache_block(mem_addr)
        return cache_block.bus_action(event, origin)

    def commit(self, ma, ic):
        self.cache_block(ma).commit(ic)

    def get_summary(self):
        summaries = [c.get_summary() for c in self._cache]
        STATS = ['hits', 'misses', 'shared_access', 'private_access']
        summary = {
            stat: sum(s[stat] for s in summaries) for stat in STATS
        }
        return summary
