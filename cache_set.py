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
    def __init__(self, cache_block_class, cache, assoc, block_id, pid):
        self.cache = cache
        self.cache_blocks =  [
            cache_block_class(cache, assoc, block_id, pid)
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

    def commit(self):
        if self.to_commit:
            self.lru.use(self.to_commit)
            self.to_commit.commit()
            self.to_commit = None

    def find_block(self, tag):
        blocks = [b for b in self.cache_blocks if b.tag == tag]
        if len(blocks) > 0:
            return blocks[0]
        else:
            return None

    def first_empty(self):
        blocks = [b for b in self.cache_blocks if b.is_empty()]
        if len(blocks) > 0:
            return blocks[0]
        else:
            return None

    def evict(self):
        cb = self.lru.evict()

        if cb.should_flush():
            cycles = 0
        else:
            cycles = 100

        cb.reset()
        return cb, cycles
