from cache import Cache
from msi_cache_block import CacheBlock

class CacheSet():
    def __init__(self, cache, n_blocks, i):
        self.cache_blocks = CacheBlock(cache.id, i)

    def get_block_for_tag(self, idx):
        return self.cache_blocks

    def get_summary(self):
        return self.cache_blocks.get_summary()

    def processor_action(self, event):
        return self.cache_blocks.processor_action(event)

    def bus_action(self, event, origin):
        return self.cache_blocks.bus_action(event, origin)

    def commit(self, ic):
        return self.cache_blocks.commit(ic)


class MsiCache(Cache):
    def init_cache_sets(self, cache_id):
        return [

            CacheSet(self, self.n_blocks, i)
            for i in range(self.n_blocks)
        ]
