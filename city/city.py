class City:
    def __init__(self, populations):
        self.populations = populations

    def tick(self):
        for group in self.populations:
            group.tick()