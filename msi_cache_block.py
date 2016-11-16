# Implementation of MSI cache coherence protocol for a single
# cache block

from debug import debug_cache_block

INVALID = 'invalid'
SHARED = 'shared'
MODIFIED = 'modified'
BUSRD = 'BusRd'
BUSRDX = 'BusRdX'
PRRD = 'PrRd'
PRWR = 'PrWr'

STATE_MACHINE = {
    INVALID: {
        PRRD: (SHARED, BUSRD, 100),
        PRWR: (MODIFIED, BUSRDX, 100),
        BUSRD: (INVALID, False, 0),
        BUSRDX: (INVALID, False, 0),
    },
    SHARED: {
        PRRD:(SHARED, None, 1),
        PRWR: (MODIFIED, BUSRDX, 1),
        BUSRD: (SHARED, False, 0),
        BUSRDX: (INVALID, False, 0),
    },
    MODIFIED: {
        PRRD: (MODIFIED, None, 0),
        PRWR: (MODIFIED, None, 0),
        BUSRD: (SHARED, True, 100),
        BUSRDX: (INVALID, True, 100),
    },
}

class CacheBlock():
    def __init__(self, cache, assoc, block_id, pid):
        self.cache = cache
        self.pid = pid
        self.cid = pid
        self.cache_set_index = block_id
        self.cache_block_index = assoc

        self.id = block_id
        self.state = INVALID
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
        return self.state == MODIFIED

    def is_empty(self):
        return self.state == INVALID

    def reset(self):
        self.state = INVALID
        self.tag = None
        self.next_state_to_commit = None
        self.pa = None
        self.ba = None
        self.next_tag = None

    def step(self, event, origin=None):
        old_state = self.state

        r = STATE_MACHINE[self.state][event]
        # self.state = r[0]
        self.next_state_to_commit = r[0]
        debug_cache_block(
            self.pid, self.cache_set_index, self.cache_block_index, old_state, event, self.next_state_to_commit, origin)
        return (old_state, r[1], r[2])

    def prrd(self, origin=None):
        self.state, bus_txn, cycles = self.step(PRRD)
        return bus_txn, cycles

    def prwr(self, origin=None):
        self.state, bus_txn, cycles = self.step(PRWR)
        return bus_txn, cycles

    def busrd(self, origin):
        self.state, snoop, cycles = self.step(BUSRD, origin)
        return snoop, cycles

    def busrdx(self, origin):
        self.state, snoop, cycles = self.step(BUSRDX, origin)
        return snoop, cycles

    def processor_action(self, event):
        self.ba = None
        self.pa = event
        return getattr(self, event.lower())()

    def bus_action(self, event, origin=None):
        self.pa = None
        self.ba = event
        return getattr(self, event.lower())(origin)

    def commit(self):
        current = self.state
        nexts = self.next_state_to_commit

        if self.next_state_to_commit:
            self.state = self.next_state_to_commit
            self.next_state_to_commit = None

        self.tag = self.next_tag
        self.next_tag = None

        if self.pa and current == INVALID:
            self.misses += 1

        if self.pa and (current == SHARED or current == MODIFIED):
            self.hits += 1

    def get_summary(self):
        return {
            'hits': self.hits,
            'misses': self.misses,
            'shared_access': self.shared_access,
            'private_access': self.private_access,
        }
