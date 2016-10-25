class Snoop():
    def __init__(self, caches):
        self.caches = caches

    def respond_to(self, bus_txn, mem_addr):
        if bus_txn is None:
            return 0
        any_snoop = False
        cmax = 0
        for c in self.caches:
            snoop, cycles = c.bus_action(bus_txn, mem_addr)
            if snoop:
                cmax = max(cmax, cycles)
                any_snoop = True
        if any_snoop:
            return cmax
        else:
            return 100
