from cache import Cache

class Simulator():
    def __init__(self, protocol, input_file, cache_size, associativity, block_size):
        self.protocol = protocol
        self.cache = Cache(
            cache_size, associativity, block_size)
