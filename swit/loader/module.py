class Module:
    __slots__ = [
        "author",
        "depend",
        "description",
        "entry",
        "name",
        "require_permission",
    ]

    def __init__(self):
        self.name = None
        self.description = None
        self.author = None
        self.entry = None
        self.depend = []
        self.require_permission = []
