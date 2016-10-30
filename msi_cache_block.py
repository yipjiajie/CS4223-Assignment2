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
        PRRD: (SHARED, BUSRD),
        PRWR: (MODIFIED, BUSRDX),
        BUSRD: (INVALID, False, 0),
        BUSRDX: (INVALID, False, 0),
    },
    SHARED: {
        PRRD:(SHARED, None),
        PRWR: (MODIFIED, BUSRDX),
        BUSRD: (SHARED, False, 0),
        BUSRDX: (INVALID, False, 0),
    },
    MODIFIED: {
        PRRD: (MODIFIED, None),
        PRWR: (MODIFIED, None),
        BUSRD: (SHARED, True, 100),
        BUSRDX: (INVALID, True, 100),
    },
}

class CacheBlock():
    def __init__(self, cache_id, block_id):
        self.cid = cache_id
        self.id = block_id
        self.state = INVALID
        self.tag = None
        self.next_state_to_commit = None
        self.hits = 0
        self.misses = 0

    def step(self, event, origin=None):
        old_state = self.state

        r = STATE_MACHINE[self.state][event]
        # self.state = r[0]
        self.next_state_to_commit = r[0]
        debug_cache_block(
            self.cid, self.id, old_state, event, self.next_state_to_commit, origin)
        if len(r) == 2:
            return (old_state, r[1])
        else:
            return (old_state, r[1], r[2])

    def prrd(self, origin=None):
        self.state, bus_txn = self.step(PRRD)
        return bus_txn

    def prwr(self, origin=None):
        self.state, bus_txn = self.step(PRWR)
        return bus_txn

    def busrd(self, origin):
        self.state, snoop, cycles = self.step(BUSRD, origin)
        return snoop, cycles

    def busrdx(self, origin):
        self.state, snoop, cycles = self.step(BUSRDX, origin)
        return snoop, cycles

    def processor_action(self, event):
        if self.state == INVALID:
            self.misses += 1
        else:
            self.hits += 1
        # invalid - prwr -> miss
        # invalid - prwr -> miss
        # shared - prrd -> hit
        # shared - prwr -> hit
        # modifed - prrd -> hit
        # modifed - prwr -> hit
        return getattr(self, event.lower())()

    def bus_action(self, event, origin=None):
        return getattr(self, event.lower())(origin)

    def commit(self):
        if self.next_state_to_commit:
            self.state = self.next_state_to_commit
            self.next_state_to_commit = None

    def get_summary(self):
        return (self.hits, self.misses)
