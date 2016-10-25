def debug_instr(ic, pn, inst, mem, bus_txn, cycles_blocked, m2):
    print('(%d)[%s#%d 0x%x] %s -> %s (blocks %d)' % (
        ic
        , pn
        , mem
        , m2
        , {'0': 'load', '1': 'store', '2': 'other'}[inst]
        , bus_txn
        , cycles_blocked
        ))

def debug_cache_block(cid, bid, old, event, new):
    print('[%s#%s] %s -%s-> %s' % (cid, bid, old, event, new))
