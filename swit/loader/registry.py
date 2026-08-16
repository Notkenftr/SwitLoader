class Registry:
    def __init__(self):
        self.modules = {}

    def add(self,name,module):
        self.modules[name] = module

    def get(self,name):
        return self.modules.get(name,None)