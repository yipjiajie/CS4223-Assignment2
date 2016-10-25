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
        BUSRDX: (INVALID, False, 10),
    },
}

class CacheBlock():
    def __init__(self, cache_id, block_id):
        self.cid = cache_id
        self.id = block_id
        self.state = INVALID
        self.tag = None

    def step(self, event):
        old_state = self.state
        r = STATE_MACHINE[self.state][event]
        self.state = r[0]
        debug_cache_block(
            self.cid, self.id, old_state, event, self.state)
        return r

    def prrd(self):
        self.state, bus_txn = self.step(PRRD)
        return bus_txn

    def prwr(self):
        self.state, bus_txn = self.step(PRWR)
        return bus_txn

    def busrd(self):
        self.state, snoop, cycles = self.step(BUSRD)
        return snoop, cycles

    def busrdx(self):
        self.state, snoop, cycles = self.step(BUSRDX)
        return snoop, cycles

    def react_to(self, event):
        return getattr(self, event.lower())()
