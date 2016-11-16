# Implementation of MSI cache coherence protocol for a single
# cache block

from cache_block import BaseCacheBlock

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

class CacheBlock(BaseCacheBlock):
    PRIVATE_STATES = [MODIFIED]
    SHARED_STATES = [SHARED]
    HAS = [MODIFIED, SHARED]
    STATE_MACHINE = STATE_MACHINE
    INITIAL_STATE = INVALID

    def initial_state(self):
        return INVALID

    def should_flush(self):
        return self.state == MODIFIED

    def is_empty(self):
        return self.state == INVALID

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
