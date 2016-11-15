class SharedLine():
    def __init__(self, caches):
        self.caches = caches

    def other_caches(self, cache_id):
        return [c for c in self.caches if c.id != cache_id]
