from cache import Cache
from msi_cache_block import CacheBlock, INVALID, SHARED
from cache_set import CacheSet


class MsiCache(Cache):
    def init_cache_sets(self, pid):
        return [
            CacheSet(CacheBlock, self, self.assoc, i, pid)
            for i in range(self.n_blocks)
        ]
