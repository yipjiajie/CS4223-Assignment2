from debug import debug_cache_block

class BaseCacheBlock():
    def __init__(self, cache, assoc, set_id, pid):
        self.cache = cache
        self.pid = pid
        self.cid = pid
        self.cache_set_index = set_id
        self.cache_block_index = assoc
        self.id = set_id
        self.state = self.INITIAL_STATE
        self.tag = None
        self.next_state_to_commit = None
        self.hits = 0
        self.misses = 0
        self.private_access = 0
        self.shared_access = 0
        self.pa = None
        self.ba = None
        self.next_tag = None

    def should_flush(self):
        raise Exception('should be overwritten')

    def is_empty(self):
        raise Exception('should be overwritten')

    def reset(self):
        self.state = self.INITIAL_STATE
        self.tag = None
        self.next_state_to_commit = None
        self.pa = None
        self.ba = None
        self.next_tag = None

    def step(self, event, origin=None):
        old_state = self.state

        r = self.STATE_MACHINE[self.state][event]
        self.next_state_to_commit = r[0]
        return (old_state, r[1], r[2])
        # self.state = r[0]
        # debug_cache_block(
            # self.pid, self.cache_set_index, self.cache_block_index, old_state, event, self.next_state_to_commit, origin)

    def processor_action(self, event):
        self.ba = None
        self.pa = event
        return getattr(self, event.lower())()

    def bus_action(self, event, origin=None):
        self.pa = None
        self.ba = event
        return getattr(self, event.lower())(origin)

    def get_summary(self):
        return {
            'hits': self.hits,
            'misses': self.misses,
            'shared_access': self.shared_access,
            'private_access': self.private_access,
        }

    def commit(self):
        if not self.next_state_to_commit:
            return
        current = self.state
        nexts = self.next_state_to_commit

        # stats
        if self.pa:

            if current == self.INITIAL_STATE:
                self.misses += 1
            else:
                self.hits += 1


            if current in self.PRIVATE_STATES:
                self.private_access += 1
            elif current in self.SHARED_STATES:
                self.shared_access += 1

        if self.next_state_to_commit:
            self.state = self.next_state_to_commit
            self.next_state_to_commit = None

        self.tag = self.next_tag
        self.next_tag = None

    def is_any_shared(self):
        return self.cache.is_any_shared(
            self.cache_set_index, self.cache_block_index, self.HAS)
