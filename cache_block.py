from debug import debug_cache_block

class BaseCacheBlock():
    def __init__(self, cache, assoc, block_id, pid):
        self.cache = cache
        self.pid = pid
        self.cid = pid
        self.cache_set_index = block_id
        self.cache_block_index = assoc

        self.id = block_id
        self.state = self.initial_state()
        self.tag = None
        self.next_state_to_commit = None
        self.hits = 0
        self.misses = 0
        self.private_access = 0
        self.shared_access = 0
        self.pa = None
        self.ba = None
        self.next_tag = None

    def initial_state(self):
        raise Exception('should be overwritten')

    def state_machine(self):
        raise Exception('should be overwritten')

    def should_flush(self):
        raise Exception('should be overwritten')

    def is_empty(self):
        raise Exception('should be overwritten')

    def reset(self):
        self.state = self.initial_state()
        self.tag = None
        self.next_state_to_commit = None
        self.pa = None
        self.ba = None
        self.next_tag = None

    def step(self, event, origin=None):
        old_state = self.state

        r = self.state_machine()[self.state][event]
        # self.state = r[0]
        self.next_state_to_commit = r[0]
        debug_cache_block(
            self.pid, self.cache_set_index, self.cache_block_index, old_state, event, self.next_state_to_commit, origin)
        return (old_state, r[1], r[2])

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
        current = self.state
        nexts = self.next_state_to_commit

        if self.pa and self.is_empty():
            self.misses += 1

        if self.pa and not self.is_empty():
            self.hits += 1


        if self.next_state_to_commit:
            self.state = self.next_state_to_commit
            self.next_state_to_commit = None

        self.tag = self.next_tag
        self.next_tag = None

