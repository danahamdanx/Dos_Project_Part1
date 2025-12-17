import time
from collections import OrderedDict

class LRUCacheTTL:
    def __init__(self, capacity=50, ttl_seconds=30):
        self.capacity = capacity
        self.ttl = ttl_seconds
        self.store = OrderedDict()  # key -> (value, expire_at)

    def get(self, key):
        now = time.time()
        if key not in self.store:
            return None
        value, exp = self.store[key]
        if exp < now:
            del self.store[key]
            return None
        self.store.move_to_end(key)
        return value

    def put(self, key, value):
        now = time.time()
        exp = now + self.ttl
        if key in self.store:
            del self.store[key]
        self.store[key] = (value, exp)
        self.store.move_to_end(key)
        if len(self.store) > self.capacity:
            self.store.popitem(last=False)

    def invalidate(self, key):
        if key in self.store:
            del self.store[key]
