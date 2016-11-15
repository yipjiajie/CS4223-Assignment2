from cache import Cache
from snoop import Snoop, BusTxn
from processor import Processor
from msi_cache import MsiCache
from debug import debug_p_tick_start, debug_bus_txn, debug_instr_pre, debug_stalls
from constants import *


class Simulator():
    def __init__(
            self,
            protocol,
            input_file,
            cache_size,
            associativity,
            block_size):
        self.protocol = protocol
        self.caches = [
            MsiCache(
                int(cache_size),
                int(associativity),
                int(block_size),
                i) for i in range(2)]
        self.processors = [
            Processor(input_file, i, self.caches[i]) for i in range(2)]
        self.snoop = Snoop(self.caches)

    def simulate(self):
        done = [False] * len(self.processors)

        while not all(done):
            for p in self.processors:
                res = p.tick()

                if res is None: # processor doing some compute or cache blocked
                    continue

                if res is True: # processor is done!
                    done[p.pn] = True
                    continue

                ic, itype, maddr = res
                mem_addr = int(maddr, 16)

                debug_instr_pre(ic, p.pn, itype, p.cache.index(mem_addr), mem_addr)

                if itype == OTHER:
                    print('[%d] itype == other' % p.pn)
                    p.compute_for(mem_addr)
                    p.proceed()
                    continue
                elif itype == LOAD:
                    pa = PrRd
                elif itype == STORE:
                    pa = PrWr
                else:
                    raise Exception('Unknown instruction')

                bus_txn, cycles = p.cache.processor_action(pa, mem_addr)

                debug_bus_txn(ic, p.pn, p.cache.index(mem_addr), bus_txn, mem_addr)

                self.snoop.add_txn(BusTxn(p.pn, bus_txn, mem_addr, cycles, p.ic))

            p_proceed = self.snoop.tick()
            for pn in p_proceed:
                self.processors[pn].proceed()

        for p in self.processors:
            print('=== Summary for processor %s ===' % p.pn)
            print(p.get_summary())
            print(p.cache.get_summary())

        print(self.snoop.get_summary())

        return 'Done'
