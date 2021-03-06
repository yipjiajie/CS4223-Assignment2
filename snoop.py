from collections import namedtuple
import random

from debug import debug_bus, debug_snoop, debug_snoop_block

BusTxn = namedtuple('BusTxn', ['pn', 'name', 'mem_addr', 'cycles', 'ic'])

class Snoop():
    def __init__(self, caches):
        self.caches = caches
        for c in caches:
            c.snoop = self
        self.txns = []
        self.traffic = 0
        self.num_invalidations = 0
        self.cycles_to_block = 0
        self.last_sel = -1

    def block_on_evict(self):
        # debug_snoop_block()
        self.cycles_to_block += 100

    def add_txn(self, txn):
        if txn is not None and txn.name is not None:
            self.txns.append(txn)

    def tick(self, p_with_mem):
        # tick 1 cycle on the snoop and returns the processors
        # that are allowed to proceed with their instructions
        # the other processors are not allowed to proceed
        if self.cycles_to_block > 0:
            self.cycles_to_block -= 1
            for c in self.caches:
                c.tick()
            self.txns = []
            return

        if not self.txns:
            for p in p_with_mem:
                p.proceed()
                p.cache.commit()
                p.cycle += 1
            return

        r = self.snoop(self.txns)
        self.txns = []

    def snoop(self, bus_txns):
        # pick 1 to respond to first (for simplicity always choose first)
        # debug_bus(bus_txns)

        sel = (self.last_sel + 1) % (len(bus_txns))
        self.last_sel = sel
        todo = bus_txns[sel]

        pn, bt, ma, cycles, ic = todo

        # only the transaction that is selected gets to commit to new stage
        self.caches[todo.pn].commit()

        # processor of the cache that is chosen to be committed can proceed
        self.caches[todo.pn].processor.proceed()

        # let every other cache to respond to a bus txn
        cycles_to_block = cycles
        # debug_snoop(pn, bt)
        for c in self.caches:
            if c.id == pn:
                continue

            snoop, cycles = c.bus_action(bt, ma, pn)
            # what kinds of  bus action can be generated by a snoop?
            # can only be a flush
            # flush blocks the entire bus for x cycles
            # assume that in this x cycles ma gets into pn's cache too
            if snoop or cycles > 0:
                self.num_invalidations += 1
                if snoop:
                    c.commit()
            cycles_to_block = max(cycles_to_block, cycles)

        # todo = bus_txns[0]
        for c in [self.caches[c.pn] for c in bus_txns]:
            c.block_for(cycles_to_block)

        if (cycles_to_block > 0):
            self.cycles_to_block = cycles_to_block
            self.traffic += 1

        return todo.pn

    def get_summary(self):
        return { 'traffic': self.traffic, 'inval': self.num_invalidations }
