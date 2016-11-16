# Implementation of Dragon cache coherence protocol for a single
# cache block

from cache_block import BaseCacheBlock

INVALID = 'invalid'

EXCLUSIVE = 'exclusive'
MODIFIED = 'modified'
SHARED_CLEAN = 'shared_clean'
SHARED_MODIFIED = 'shared_modified'

PRRDMISS ='prrdmiss'
PRRD_TO_SC = 'prrd_to_sc'
PRRD_TO_E = 'prrd_to_e'
PRWR_I_TO_M = 'prwr_i_to_m'
PRWR_I_TO_SM = 'prwr_i_to_sm'
PRWR_SM_TO_SM = 'prwr_sm_to_sm'
PRWR_SM_TO_M = 'prwr_sm_to_m'
PRWR_M_TO_M = 'prwr_m_to_m'

BUSRD = 'BusRd'
PRRD = 'PrRd'
PRWR = 'PrWr'
BUSUPD = ' BusUpd'


STATE_MACHINE = {
    INVALID: {
        PRRD_TO_SC: (SHARED_CLEAN, None, 100),
        PRRD_TO_E: (EXCLUSIVE, None, 100),
        PRWR_I_TO_M: (MODIFIED, None, 100),
        PRWR_I_TO_SM: (SHARED_MODIFIED, None, 100),

        BUSRD: (INVALID, False, 0),
    },
    EXCLUSIVE: {
        PRRD: (EXCLUSIVE, None, 1),
        PRWR: (MODIFIED, None, 1),

        BUSRD: (SHARED_CLEAN, None, 0),
    },
    SHARED_CLEAN: {
        PRRD: (SHARED_CLEAN, None, 1),
        PRWR: (SHARED_MODIFIED, BUSUPD, 1),

        BUSRD: (SHARED_CLEAN, None, 0),
        BUSUPD: (SHARED_CLEAN, None, 100),
    },
    SHARED_MODIFIED: {
        PRRD: (SHARED_MODIFIED, None, 1),
        PRWR_SM_TO_SM: (SHARED_MODIFIED, BUSUPD, 1),
        PRWR_SM_TO_M: (MODIFIED, None, 1),

        BUSUPD: (SHARED_CLEAN, None, 100),
        BUSRD: (SHARED_MODIFIED, None, 100),
    },

    MODIFIED: {
        PRRD: (MODIFIED, None, 0),
        PRWR: (MODIFIED, None, 0),
        PRWR_M_TO_M: (MODIFIED, None, 0),

        BUSRD: (SHARED_MODIFIED, True, 100),
    },
}

class CacheBlock(BaseCacheBlock):
    def state_machine(self):
        return STATE_MACHINE

    def initial_state(self):
        return INVALID

    def should_flush(self):
        return self.state == MODIFIED

    def is_empty(self):
        return self.state == INVALID

    def shared_states(self):
        return [MODIFIED, SHARED_CLEAN, SHARED_MODIFIED]

    def prrd(self, origin=None):
        if self.state == INVALID and self.is_any_shared():
            self.state, bus_txn, cycles = self.step(PRRD_TO_SC)
        elif self.state == INVALID and not self.is_any_shared():
            self.state, bus_txn, cycles = self.step(PRRD_TO_E)
        else:
            self.state, bus_txn, cycles = self.step(PRRD)
        return bus_txn, cycles

    def prwr(self, origin=None):
        if self.state == SHARED_MODIFIED and self.is_any_shared():
            self.state, bus_txn, cycles = self.step(PRWR_SM_TO_SM)
        elif self.state == SHARED_MODIFIED and not self.is_any_shared():
            self.state, bus_txn, cycles = self.step(PRWR_SM_TO_M)
        elif self.state == INVALID and self.is_any_shared():
            self.state, bus_txn, cycles = self.step(PRWR_I_TO_SM)
        elif self.state == INVALID and not self.is_any_shared():
            self.state, bus_txn, cycles = self.step(PRWR_I_TO_M)
        elif self.state == MODIFIED and not self.is_any_shared():
            self.state, bus_txn, cycles = self.step(PRWR_M_TO_M)
        else:
            self.state, bus_txn, cycles = self.step(PRWR)
        return bus_txn, cycles

    def busrd(self, origin):
        self.state, snoop, cycles = self.step(BUSRD, origin)
        return snoop, cycles
