## Files

`coherence` top level file that accepts command line parameters

`simulator.py` runs the simulation

`processor.py` signifies a processor under simulation

`reader.py` used by processor to read instructions from `data/`

`cache.py` base cache class that specific protocols should inherit from

`msi_cache.py` cache that implements the MSI protocol

`msi_cache_block.py` cache_block used by `msi_cache.py`

`snoop.py` the bus that cache controllers use to snoop on bus transactions

`data/testdata/` a subset of provided data for quicker testing

## Running tests
Simple runner to just run smoke tests:

```
make test
```

What works now is

```
./coherence MSI testdata 1024 1 16
```

## TODO
Validate that MSI actually works
Implement MESI and Dragon
More stats:

1. Data cache miss rate for each core
2. Amount of Data traffic in bytes on the bus (this is due to bus read, bus write, and bus update transactions)
3. Number of invalidations or updates on the bus
4. Distribution of accesses to private data versus shared data (for example, access to modified state is private, while access to shared state is shared data)
5. Average write latency
6. Execution Cycles (different core will complete at different cycles; report the maximum value across all cores)
