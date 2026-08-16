class Module:
    __slots__ = ["name","description","entry","depend","author","require_permission"]
    def __init__(self):
        self.name = None
        self.description = None
        self.author = None
        self.entry = None
        self.depend = []
        self.require_permission = []