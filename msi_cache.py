from cache import Cache
from msi_cache_block import CacheBlock, INVALID

class LRUEviction():
    def __init__(self, members):
        self.members = members
        self.last_count = {
            m: 0 for m in members
        }
        self.cur_max = 0

    def use(self, m):
        self.last_count[m] = self.cur_max + 1
        self.cur_max += 1

    def evict(self):
        min_ = self.cur_max
        min_member = None
        for memb, count in self.last_count.items():
            if count <= min_:
                min_ = count
                min_member = memb
        return min_member


class CacheSet():
    def __init__(self, cache, assoc, i):
        self.cache_blocks =  [
            CacheBlock(assoc, i)
            for i in range(assoc)
        ]
        self.to_commit = None
        self.lru = LRUEviction(self.cache_blocks)

    def get_summary(self):
        summaries = [c.get_summary() for c in self.cache_blocks]
        STATS = ['hits', 'misses', 'shared_access', 'private_access']
        summary = {
                stat: sum(s[stat] for s in summaries) for stat in STATS
        }
        return summary

    def commit(self, tag, ic):
        if self.to_commit is None:
            raise Exception('tomcommit is none')
        else:
            self.lru.use(self.to_commit)
            self.to_commit.commit(ic)

    def find_block(self, tag):
        blocks = [b for b in self.cache_blocks if b.tag == tag]
        if len(blocks) > 0:
            return blocks[0]
        else:
            return None

    def first_empty(self):
        blocks = [b for b in self.cache_blocks if b.state == INVALID]
        if len(blocks) > 0:
            return blocks[0]
        else:
            return None

    def evict(self):
        cb = self.lru.evict()
        cb.reset()
        return cb


class MsiCache(Cache):
    def init_cache_sets(self, cache_id):
        return [

            CacheSet(self, self.assoc, i)
            for i in range(self.n_blocks)
        ]
