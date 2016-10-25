# Implementation of MSI cache coherence protocol for a single
# cache block

INVALID = 'invalid'
SHARED = 'shared'
MODIFIED = 'modified'
BUSRD = 'busrd'
BUSRDX = 'busrdx'
PRRD = 'prrd'
PRWR = 'prwr'

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
    def __init__(self):
        self.state = INVALID
        self.tag = None

    def prrd(self):
        self.state, bus_txn = STATE_MACHINE[self.state][PRRD]
        return bus_txn

    def prwr(self):
        self.state, bus_txn = STATE_MACHINE[self.state][PRWR]
        return bus_txn

    def busrd(self):
        self.state, snoop, cycles = STATE_MACHINE[self.state][BUSRD]
        return snoop, cycles

    def busrdx(self):
        self.state, snoop, cycles = STATE_MACHINE[self.state][BUSRDX]
        return snoop, cycles

    def react_to(self, event):
        return getattr(self, event)()
