from cache import Cache
from msi_cache_block import CacheBlock

class MsiCache(Cache):
    def init_cache_blocks(self):
        return [CacheBlock() for i in range(self.n_blocks)]

