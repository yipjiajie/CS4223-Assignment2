import os

if 'DEBUG' in os.environ:
    debug = lambda x: print(x)
else:
    debug = lambda x: x

def debug_p_tick_start():
    debug('PROCESSOR TICK START====')

def debug_instr_pre(ic, pn, inst, mem, m2):
    debug('IPRE: [%s][#%2d 0x%x] (%d) %s' % (
        pn
        , mem
        , m2
        , ic
        , {'0': 'load', '1': 'store', '2': 'other'}[inst]
        ))

def debug_bus_txn(ic, pn, mem, bus_txn, m2):
    debug('B: [%s][#%2d 0x%x] (%d) next: %s' % (
        pn
        , mem
        , m2
        , ic
        , bus_txn
        ))

def debug_cache_block(cid, bid, old, event, new, origin=None):
    if origin:
        debug('C: [%s][#%2s] %s -%s-> %s from [%s]' % (cid, bid, old, event, new, origin))
    else:
        debug('C: [%s][#%2s] %s -%s-> %s' % (cid, bid, old, event, new))

def debug_stalls(pn, stall_count):
    debug('T: [%s] (%d)' % (
        pn
        , stall_count
        ))

def debug_snoop(pn, bt):
    debug('S: arbritary selected %s from %s' % (bt, pn))

def debug_cache(cid, cycles, total):
    debug('$: [%s] blocking for %s, total now %s' % (cid, cycles, total))

def debug_bus(bus_txns):
    debug('=== Bus ===')
    debug(bus_txns)
