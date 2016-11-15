from cache import Cache
from mesi_cache_block import CacheBlock

class MesiCache(Cache):
    def init_cache_blocks(self, cache_id):
        return [CacheBlock(cache_id, i) for i in range(self.n_blocks)]

