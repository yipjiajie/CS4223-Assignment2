from cache import Cache
from snoop import Snoop, BusTxn
from processor import Processor
from msi_cache import MsiCache
from dragon_cache import DragonCache
from mesi_cache import MesiCache
from debug import debug_bus_txn, debug_instr_pre
from constants import *
from shared_line import SharedLine


class Simulator():
    def __init__(
            self,
            protocol,
            input_file,
            cache_size,
            associativity,
            block_size):
        self.protocol = protocol
        if self.protocol == 'msi':
            cache_class = MsiCache
        elif self.protocol == 'mesi':
            cache_class = MesiCache
        elif self.protocol == 'dragon':
            cache_class = DragonCache

        self.caches = [
            cache_class(
                int(cache_size),
                int(associativity),
                int(block_size),
                i) for i in range(4)]

        if self.protocol == 'mesi' or self.protocol == 'dragon':
            shared_line = SharedLine(self.caches)
            for c in self.caches:
                c.set_shared_line(shared_line)

        self.processors = [
            Processor(input_file, i, self.caches[i]) for i in range(4)]
        self.snoop = Snoop(self.caches)

    def simulate(self):
        done = [False] * len(self.processors)

        while not all(done):
            for p in self.processors:

                if p.done:
                    continue

                res = p.tick()

                if res is None: # processor doing some compute or cache blocked
                    continue

                if res is True: # processor is done!
                    done[p.pn] = True
                    continue

                ic, itype, maddr = res
                mem_addr = int(maddr, 16)

                # debug_instr_pre(ic, p.pn, itype, p.cache.index(mem_addr), mem_addr)

                if itype == OTHER:
                    p.compute_for(mem_addr)
                    # p.proceed()
                    continue
                elif itype == LOAD:
                    pa = PrRd
                elif itype == STORE:
                    pa = PrWr
                else:
                    raise Exception('Unknown instruction')

                if self.snoop.cycles_to_block <= 0:
                    bus_txn, cycles = p.cache.processor_action(pa, mem_addr)

                    if bus_txn == 'EVICT':
                        self.snoop.block_on_evict()
                    else:
                        self.snoop.add_txn(BusTxn(p.pn, bus_txn, mem_addr, cycles, p.ic))

            self.snoop.tick()

        for p in self.processors:
            print('=== Summary for processor %s ===' % p.pn)
            print(p.get_summary())
            print(p.cache.get_summary())

        print(self.snoop.get_summary())

        return 'Done'
