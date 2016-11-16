from cache import Cache
from dragon_cache_block import CacheBlock
from cache_set import CacheSet


class DragonCache(Cache):
    def init_cache_sets(self, pid):
        return [
            CacheSet(CacheBlock, self, self.assoc, i, pid)
            for i in range(self.n_blocks)
        ]
