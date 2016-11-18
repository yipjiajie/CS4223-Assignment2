# Implementation of Dragon cache coherence protocol for a single
# cache block

from cache_block import BaseCacheBlock

INVALID = 'invalid'

CLEAN = 'clean'
MODIFIED = 'modified'
SHARED_CLEAN = 'shared_clean'
SHARED_MODIFIED = 'shared_modified'

PRRDMISS ='prrdmiss'
PRRD_TO_SC = 'prrd_to_sc'
PRRD_TO_C = 'prrd_to_c'
PRWR_I_TO_M = 'prwr_i_to_m'
PRWR_I_TO_SM = 'prwr_i_to_sm'
PRWR_SM_TO_SM = 'prwr_sm_to_sm'
PRWR_SM_TO_M = 'prwr_sm_to_m'
PRWR_M_TO_M = 'prwr_m_to_m'
PRWR_M_TO_SM = 'prwr_m_to_sm'
PRWR_SC_TO_SM = 'prwr_sc_to_sm '
PRWR_SC_TO_M = 'prwr_sc_to_m '

BUSRD = 'busrd'
BUSRDSC = 'busrdsc'
BUSRD_E = 'BusRdE'
PRRD = 'PrRd'
PRWR = 'PrWr'
BUSUPD = 'BusUpd'
WRITE_BC = 'WriteBc'
BUS_SC_TO_SM = 'bus_sc_to_sm'


STATE_MACHINE = {
    INVALID: {
        PRRD_TO_SC: (SHARED_CLEAN, BUSRDSC, 100),
        PRRD_TO_C: (CLEAN, BUSRD, 100),
        PRWR_I_TO_M: (MODIFIED, BUSRD, 100),
        PRWR_I_TO_SM: (SHARED_MODIFIED, WRITE_BC, 100),

        BUSRDSC: (INVALID, False, 0),
        BUSUPD: (INVALID, False, 0),
        WRITE_BC: (INVALID, False, 0),
    },
    CLEAN: {
        PRRD: (CLEAN, None, 1),
        PRWR: (MODIFIED, None, 1),

        BUSRDSC: (SHARED_CLEAN, True, 0),
        WRITE_BC: (SHARED_CLEAN, True, 100),
    },
    SHARED_CLEAN: {
        PRRD: (SHARED_CLEAN, None, 1),
        PRWR: (SHARED_MODIFIED, BUSUPD, 1),
        PRWR_SC_TO_M : (MODIFIED, None, 1),
        PRWR_SC_TO_SM : (SHARED_MODIFIED, BUS_SC_TO_SM, 1),

        BUSRDSC: (SHARED_CLEAN, True, 100),
        BUSUPD: (SHARED_CLEAN, True, 100),
        WRITE_BC: (SHARED_CLEAN, True, 100),
        BUS_SC_TO_SM: (SHARED_CLEAN, True, 100),
    },
    SHARED_MODIFIED: {
        PRRD: (SHARED_MODIFIED, None, 1),
        PRWR_SM_TO_SM: (SHARED_MODIFIED, BUSUPD, 1),
        PRWR_SM_TO_M: (MODIFIED, None, 1),

        BUSUPD: (SHARED_CLEAN, True, 100),
        BUSRDSC: (SHARED_MODIFIED, True, 100),
        WRITE_BC: (SHARED_CLEAN, True, 100),
        BUS_SC_TO_SM: (SHARED_CLEAN, True, 100),
    },

    MODIFIED: {
        PRRD: (MODIFIED, None, 0),
        PRWR: (MODIFIED, None, 0),
        # PRWR_M_TO_M: (MODIFIED, None, 0),
        # PRWR_M_TO_SM: (SHARED_MODIFIED, None, 100),

        BUSRDSC: (SHARED_MODIFIED, True, 100),
        WRITE_BC: (SHARED_CLEAN, True, 100),
        BUS_SC_TO_SM: (SHARED_CLEAN, True, 100),
    },
}

class CacheBlock(BaseCacheBlock):
    PRIVATE_STATES = [CLEAN, MODIFIED]
    SHARED_STATES = [SHARED_CLEAN, SHARED_MODIFIED]
    HAS = [CLEAN, MODIFIED, SHARED_CLEAN, SHARED_MODIFIED]
    STATE_MACHINE = STATE_MACHINE
    INITIAL_STATE = INVALID

    def initial_state(self):
        return INVALID

    def should_flush(self):
        return self.state == MODIFIED

    def is_empty(self):
        return self.state == INVALID

    def prrd(self, origin=None):
        if self.state == INVALID:
            if self.is_any_shared():
                self.state, bus_txn, cycles = self.step(PRRD_TO_SC)
            else:
                self.state, bus_txn, cycles = self.step(PRRD_TO_C)
        else:
            self.state, bus_txn, cycles = self.step(PRRD)
        return bus_txn, cycles

    def prwr(self, origin=None):
        if self.state == SHARED_MODIFIED:
            if self.is_any_shared():
                self.state, bus_txn, cycles = self.step(PRWR_SM_TO_SM)
            else:
                self.state, bus_txn, cycles = self.step(PRWR_SM_TO_M)
        elif self.state == SHARED_CLEAN:
            if self.is_any_shared():
                self.state, bus_txn, cycles = self.step(PRWR_SC_TO_SM)
            else:
                self.state, bus_txn, cycles = self.step(PRWR_SC_TO_M)
        elif self.state == INVALID:
            if self.is_any_shared():
                self.state, bus_txn, cycles = self.step(PRWR_I_TO_SM)
            else:
                self.state, bus_txn, cycles = self.step(PRWR_I_TO_M)
        # elif self.state == MODIFIED:
        #     if not self.is_any_shared():
        #         self.state, bus_txn, cycles = self.step(PRWR_M_TO_M)
        #     else:
        #         self.state, bus_txn, cycles = self.step(PRWR_M_TO_SM)
        else:
            self.state, bus_txn, cycles = self.step(PRWR)
        return bus_txn, cycles

    def busrd(self, origin):
        self.state, snoop, cycles = self.step(BUSRD, origin)
        return snoop, cycles

    def busrdsc(self, origin):
        self.state, snoop, cycles = self.step(BUSRDSC, origin)
        return snoop, cycles

    def busupd(self, origin):
        self.state, snoop, cycles = self.step(BUSUPD, origin)
        return snoop, cycles

    def writebc(self, origin):
        self.state, snoop, cycles = self.step(WRITE_BC, origin)
        return snoop, cycles

    def bus_sc_to_sm(self, origin):
        self.state, snoop, cycles = self.step(BUS_SC_TO_SM, origin)
        return snoop, cycles
