def debug_instr_pre(ic, pn, inst, mem, m2):
    print('I: [%s][#%2d 0x%x] (%d) %s' % (
        pn
        , mem
        , m2
        , ic
        , {'0': 'load', '1': 'store', '2': 'other'}[inst]
        ))

def debug_bus_txn(ic, pn, mem, bus_txn, m2):
    print('B: [%s][#%2d 0x%x] (%d) next: %s' % (
        pn
        , mem
        , m2
        , ic
        , bus_txn
        ))

def debug_cache_block(cid, bid, old, event, new, origin=None):
    if origin:
        print('C: [%s][#%2s] %s -%s-> %s from [%s]' % (cid, bid, old, event, new, origin))
    else:
        print('C: [%s][#%2s] %s -%s-> %s' % (cid, bid, old, event, new))

def debug_stalls(pn, stall_count):
    print('T: [%s] (%d)' % (
        pn
        , stall_count
        ))

def debug_snoop(pn, bt):
    print('S: arbritary selected %s from %s' % (bt, pn))

def debug_cache(cid, cycles, total):
    print('$: [%s] blocking for %s, total now %s' % (cid, cycles, total))
