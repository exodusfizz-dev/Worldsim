class City:
    def __init__(self, populations):
        self.populations = populations

    def tick(self):
        for group in self.populations:
            group.tick()        
        self.total_population = sum(group.size for group in self.populations)