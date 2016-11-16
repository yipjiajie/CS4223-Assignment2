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

    def is_any_shared(self, set_id, block_id):
        for c in self.shared_line.other_caches(self.id):
            if self.cache_sets[set_id].block_by_index(block_id) in [MODIFIED, EXCLUSIVE]:
                return True
        return False

