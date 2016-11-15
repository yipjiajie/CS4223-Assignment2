from cache import Cache
from msi_cache_block import CacheBlock

class CacheSet():
    def __init__(self, cache, assoc, i):
        self.cache_blocks =  [
            CacheBlock(assoc, i)
            for i in range(assoc)
        ]

    def get_block_for_tag(self, idx):
        return self.cbr()

    def get_summary(self):
        return self.cbr().get_summary()

    def processor_action(self, event):
        return self.cbr().processor_action(event)

    def bus_action(self, event, origin):
        return self.cbr().bus_action(event, origin)

    def commit(self, ic):
        return self.cbr().commit(ic)

    def cbr(self):
        # Choose correct block
        return self.cache_blocks[0]


class MsiCache(Cache):
    def init_cache_sets(self, cache_id):
        return [

            CacheSet(self, self.assoc, i)
            for i in range(self.n_blocks)
        ]
