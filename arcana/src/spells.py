from abc import ABC, abstractmethod
from enum import Enum


class Rarity(Enum):
    COMMON = "common"
    RARE = "rare"
    LEGENDARY = "legendary"


class Spell(ABC):
    def __init__(self, name, cost, rarity):
        self.name = name
        self.cost = cost
        self.rarity = rarity

    @abstractmethod
    def cast(self, caster, target):
        pass

    @abstractmethod
    def describe(self):
        pass

    def __gt__(self, other):
        order = [Rarity.COMMON, Rarity.RARE, Rarity.LEGENDARY]
        return order.index(self.rarity) > order.index(other.rarity)


class WeaveSpell(Spell):
    def __init__(self, name, cost, rarity=Rarity.COMMON):
        super().__init__(name, cost, rarity)

    def cast(self, caster, target):
        caster.energy -= self.cost
        return f"{caster} wove a connection to {target} [{self.name}]"

    def describe(self):
        return f"Weave spell '{self.name}', cost={self.cost}"


class CutSpell(Spell):
    def __init__(self, name, cost, severity, rarity=Rarity.COMMON):
        super().__init__(name, cost, rarity)
        self.severity = severity

    def cast(self, caster, target):
        caster.energy -= self.cost
        return f"{caster} cut {target}'s stability by {self.severity} [{self.name}]"

    def describe(self):
        return f"Cut spell '{self.name}', severity={self.severity}"


class BindSpell(Spell):
    def __init__(self, name, cost, duration, rarity=Rarity.RARE):
        super().__init__(name, cost, rarity)
        self.duration = duration

    def cast(self, caster, target):
        caster.energy -= self.cost
        return f"{caster} bound {target} for {self.duration} turns [{self.name}]"

    def describe(self):
        return f"Bind spell '{self.name}', duration={self.duration}"


class LegendaryWeaveSpell(WeaveSpell):
    def __init__(self, name, cost):
        super().__init__(name, cost, Rarity.LEGENDARY)

    def cast(self, caster, target):
        base = super().cast(caster, target)
        return f"[LEGENDARY] {base} (x2 power)"

    def describe(self):
        return f"Legendary weave '{self.name}', cost={self.cost}"


class CombinedSpell(Spell):
    def __init__(self, name, spells):
        total_cost = sum(s.cost for s in spells)
        super().__init__(name, total_cost, Rarity.RARE)
        self.spells = spells

    def cast(self, caster, target):
        results = []
        for spell in self.spells:
            results.append(spell.cast(caster, target))
        return " | ".join(results)

    def describe(self):
        return f"Combined spell '{self.name}' with {len(self.spells)} sub-spells"


# MRO for LegendaryWeaveSpell:
# LegendaryWeaveSpell -> WeaveSpell -> Spell -> ABC -> object
print(LegendaryWeaveSpell.__mro__)
