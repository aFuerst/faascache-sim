class LambdaData:
    def __init__ (self, kind, mem_size, run_time, warm_time):
        self.kind = kind 
        self.mem_size = mem_size
        self.run_time = run_time 
        self.warm_time = warm_time
        
    #def __init__(self, idx:int):
    #    self.kind = self.kinds[idx]
    #    self.mem_size = self.mem_sizes[idx]
    #    self.run_time = self.run_times[idx]
    #    self.warm_time = self.warm_times[idx]

        
    def __eq__(self, other):
        if isinstance(other, LambdaData):
            return self.kind == other.kind 
        
    def __repr__(self):
        return str((self.kind, self.mem_size))