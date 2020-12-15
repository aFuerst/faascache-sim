from LambdaData import LambdaData

class Container:
    
    last_access_t = 0
    pre_warmed_t = 0
    keep_alive_start_t = 0
    in_cache = False 
    frequency = 0 #Number of in-cache accesses (Streak)
    state = "COLD"
    
    def __init__(self, lamdata: LambdaData):
        self.metadata = lamdata 
        self.Priority = 0 #Used for the Greedy dual size eviction 
        self.insert_clock = 0 #When was this inserted... 
        
    def prewarm(self):
        self.state = "WARM"
    
    def cfree(self):
        return self.state == "WARM" or self.state == "COLD"
    
    def run(self):
        #returns the time when finished? 
        self.in_cache = True 
        self.state = "RUNNING"
        self.frequency += 1 
        
    def terminate(self):
        self.in_cache = False 
        self.frequency = 0 
        self.state = "TERM"
        
    def __lt__(self, other):
         return self.Priority < other.Priority
    
    def __repr__(self):
        return str((self.metadata.kind, self.Priority))