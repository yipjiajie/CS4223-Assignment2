from math import log
from msi_cache_block import CacheBlock
from debug import debug_cache

def log2(x): return int(log(x, 2))

class Cache():
    def __init__(self, cache_size, assoc, block_size, pn):
        self.snoop = None # will be set by snoop later
        self.processor = None
        self.id = pn
        self.pid = pn
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

        self.cache_sets = self.init_cache_sets(self.pid)
        self._blocked_for = 0
        self.to_commit = None

    def init_cache_sets(self, cid):
        return []

    def offset(self, mem_addr):
        return mem_addr & self.offset_mask

    def index(self, mem_addr):
        return (mem_addr >> self.n_bits_offset) & self.index_mask

    def tag(self, mem_addr):
        return mem_addr >> (self.n_bits_offset + self.n_bits_index)

    def cache_set(self, mem_addr):
        return self.cache_sets[self.index(mem_addr)]

    def cache_block(self, mem_addr):
        return self.cache_set(mem_addr).find_block(self.tag(mem_addr))

    def tick(self):
        if self._blocked_for > 0:
            self._blocked_for -= 1

    def block_for(self, cycles):
        self._blocked_for += cycles
        # debug_cache(self.id, cycles, self._blocked_for)

    def processor_action(self, event, mem_addr):
        """Respond to a processor action.

        Returns bus_txn:
            the name of bus event triggered
        """
        cs = self.cache_set(mem_addr)
        self.cs_to_commit = cs

        cb = self.cache_block(mem_addr)
        # found cache block with same tag
        if cb:
            cb.next_tag = self.tag(mem_addr)
            cs.to_commit = cb
            return cb.processor_action(event)

        cb = cs.first_empty()
        if cb:
            cb.next_tag = self.tag(mem_addr)
            cs.to_commit = cb
            return cb.processor_action(event)
        else:
            # no empty cache block
            cb, cycles = cs.evict()
            cb.next_tag = self.tag(mem_addr)
            cs.to_commit = cb

            return 'EVICT', cycles

    def bus_action(self, event, mem_addr, origin):
        """Respond to a bus snoop action

        Returns (snoop, cycles to block):
            snoop is a boolean indicating if the cache block snooped this event
            cycles to block indicates cycles that the cache controll is blocked
        """
        cb = self.cache_block(mem_addr)

        if not cb:
            return None, 0

        return cb.bus_action(event, origin)
        # cache_set = self.cache_set(mem_addr)
        # return cache_set.bus_action(event, origin)

    def commit(self):
        if self.cs_to_commit:
            self.cs_to_commit.commit()
            self.cs_to_commit = None

    def get_summary(self):
        summaries = [c.get_summary() for c in self.cache_sets]
        STATS = ['hits', 'misses', 'shared_access', 'private_access']
        summary = {
            stat: sum(s[stat] for s in summaries) for stat in STATS
        }
        return summary

    def set_shared_line(self, shared_line):
        self.shared_line = shared_line

    def is_any_shared(self, set_id, block_id, shared_states):
        for c in self.shared_line.other_caches(self.id):
            if self.cache_sets[set_id].block_by_index(block_id) in shared_states:
                return True
        return False
