from cache import Cache
from mesi_cache_block import CacheBlock, MODIFIED, EXCLUSIVE
from cache_set import CacheSet

class MesiCache(Cache):
    def init_cache_sets(self, pid):
        return [
            CacheSet(CacheBlock, self, self.assoc, i, pid)
            for i in range(self.n_blocks)
        ]

    def set_shared_line(self, shared_line):
        self.shared_line = shared_line

    def is_any_shared(self, block_id):
        for c in self.shared_line.other_caches(self.id):
            if c.has_block(block_id):
                return True
        return False

    def has_block(self, block_id):
        return self._cache[block_id].state in [MODIFIED, EXCLUSIVE]
