## Running simulator

With the data files unzipped in the `data` direcory, running the code is just

```
./coherence MSI blackscholes 1024 1 16
```

The trace files must be in the data folder, for example:

```
- README.md
- data/
  - blackscholes/
      - blackscholes_0.data
      - blackscholes_1.data
      - blackscholes_2.data
      - blackscholes_3.data
- simulator.py
...
```

## Important files

`coherence` top level file that accepts command line parameters

`simulator.py` runs the simulation

`processor.py` signifies a processor under simulation

`reader.py` used by processor to read instructions from `data/`

`cache.py` base cache class that specific protocols should inherit from

`msi_cache.py` cache that implements the MSI protocol

`msi_cache_block.py` cache_block used by `msi_cache.py`

`mesi_cache.py` cache that implements the MESI protocol

`mesi_cache_block.py` cache_block used by `mesi_cache.py`

`dragon_cache.py` cache that implements the Dragon protocol

`dragon_cache_block.py` cache_block used by `dragon_cache.py`

`snoop.py` the bus that cache controllers use to snoop on bus transactions

`shared_line.py` shared_line used by caches to chck if cache block is in other caches
