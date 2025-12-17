class RoundRobin:
    def __init__(self, urls):
        self.urls = [u.strip() for u in urls if u.strip()]
        self.i = 0

    def next(self):
        if not self.urls:
            raise RuntimeError("No replicas configured")
        url = self.urls[self.i % len(self.urls)]
        self.i += 1
        return url
