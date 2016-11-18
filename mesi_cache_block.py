# Implementation of MESI cache coherence protocol for a single
# cache block

from debug import debug_cache_block
from cache_block import BaseCacheBlock

INVALID = 'invalid'
SHARED = 'shared'
MODIFIED = 'modified'
EXCLUSIVE = 'exclusive'
BUSRD = 'BusRd'
BUSRDX = 'BusRdX'
PRRD = 'PrRd'
PRRDS = 'PrRdS'
PRWR = 'PrWr'

STATE_MACHINE = {
    INVALID: {
        PRRD: (EXCLUSIVE, BUSRD, 100),
        PRRDS: (SHARED, BUSRD, 100),
        PRWR: (MODIFIED, BUSRDX, 100),
        BUSRD: (INVALID, False, 0),
        BUSRDX: (INVALID, False, 0),
    },
    SHARED: {
        PRRD: (SHARED, None, 1),
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
    EXCLUSIVE: {
        PRRD: (EXCLUSIVE, None, 0),
        PRWR: (MODIFIED, None, 0),
        BUSRD: (SHARED, True, 100),
        BUSRDX: (INVALID, True, 100),
    }
}

class CacheBlock(BaseCacheBlock):
    PRIVATE_STATES = [MODIFIED, EXCLUSIVE]
    SHARED_STATES = [SHARED]
    HAS = [EXCLUSIVE, MODIFIED, SHARED]
    STATE_MACHINE = STATE_MACHINE
    INITIAL_STATE = INVALID

    def initial_state(self):
        return INVALID

    def should_flush(self):
        return self.state == MODIFIED

    def is_empty(self):
        return self.state == INVALID

    def prrd(self, origin=None):
        # find out if any other cache has exclusive or modified
        # if so: then i go to shared
        # otherwise i go to exclusive
        if self.state == INVALID and self.is_any_shared():
            self.state, bus_txn, cycles = self.step(PRRDS)
        else:
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
