def debug_instr(pn, inst, mem, bus_txn, cycles_blocked):
    print('P[%s] %s from %d gen %s (blocks %d)' %
            (  pn
             , {'0': 'load', '1': 'store', '2': 'other'}[inst]
             , mem
             , bus_txn
             , cycles_blocked
             ))

def debug_cache_block(cid, bid, old, event, new):
    print('[%s#%s] %s -%s-> %s' % (cid, bid, old, event, new))
