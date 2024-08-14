

class State:
    def __init__(self, name: str):
        self.name = name

    @property
    def START(self):
        return self.name + "_START"

    @property
    def END(self):
        return self.name + "_END"