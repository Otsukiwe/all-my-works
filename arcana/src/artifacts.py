from abc import ABC, abstractmethod


class Artifact(ABC):
    def __init__(self, durability):
        self.__durability = durability

    @property
    def durability(self):
        return self.__durability

    @durability.setter
    def durability(self, value):
        self.__durability = max(0, value)

    @abstractmethod
    def activate(self, thread):
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(durability={self.__durability})"


class CrystalCore(Artifact):
    def __init__(self):
        super().__init__(100)

    def activate(self, thread):
        self.durability -= 2
        return thread.frequency * thread.stability * 1.5


class RuneMatrix(Artifact):
    def __init__(self, capacity=5):
        super().__init__(100)
        self.capacity = capacity
        self._stored = []

    def store(self, thread):
        if len(self._stored) < self.capacity:
            self._stored.append(thread)

    def activate(self, thread):
        self.durability -= 1
        total = sum(t.frequency * t.stability for t in self._stored)
        return total
