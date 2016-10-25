from cache import Cache
from snoop import Snoop
from processor import Processor
from msi_cache import MsiCache
from debug import debug_instr

LOAD = '0'
STORE = '1'
OTHER = '2'
PrRd = 'PrRd'
PrWr = 'PrWr'

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
        print("simulating...")
        done = [False] * len(self.processors)
        while not all(done):
            for p in self.processors:
                if done[p.pn]:
                    continue

                ic, ity, maddr = p.fetch_instr() # advance by 1 cycle

                if ity is None:
                    done[p.pn] = True
                    continue

                if ity == True:
                    continue

                mem_addr = int(maddr, 16)
                if ity == LOAD:
                    bus_txn = p.cache.processor_action(PrRd, mem_addr)
                    cycles_needed = self.snoop.respond_to(bus_txn, mem_addr, p.cache.id)
                    debug_instr(ic, p.pn, ity, p.cache.index(mem_addr), bus_txn, cycles_needed, mem_addr)
                    p.memory_access_for(cycles_needed)
                elif ity == STORE:
                    bus_txn = p.cache.processor_action(PrWr, mem_addr)
                    cycles_needed = self.snoop.respond_to(bus_txn, mem_addr, p.cache.id)
                    debug_instr(ic, p.pn, ity, p.cache.index(mem_addr), bus_txn, cycles_needed, mem_addr)
                    p.memory_access_for(cycles_needed)
                elif ity == OTHER:
                    num_cycles = mem_addr
                    debug_instr(ic, p.pn, ity, p.cache.index(mem_addr), None, num_cycles, mem_addr)
                    p.compute_for(num_cycles)
        for p in self.processors:
            print(p.get_summary())
        return 'Done'
