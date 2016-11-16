from cache import Cache
from mesi_cache_block import CacheBlock, MODIFIED, EXCLUSIVE
from cache_set import CacheSet

class MesiCache(Cache):
    def init_cache_sets(self, pid):
        return [
            CacheSet(CacheBlock, self, self.assoc, i, pid)
            for i in range(self.n_blocks)
        ]
