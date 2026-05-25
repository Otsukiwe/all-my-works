from typing import Protocol, runtime_checkable


@runtime_checkable
class ArcaneInterface(Protocol):
    def cast(self, caster, target) -> str: ...
    def describe(self) -> str: ...


class Caster:
    def __init__(self, name, energy, artifact=None):
        self.name = name
        self.energy = energy
        self.artifact = artifact
        self.__spell_book = {}

    def learn(self, spell):
        self.__spell_book[spell.name] = spell

    def forget(self, spell_name):
        self.__spell_book.pop(spell_name, None)

    def cast(self, spell_name, target):
        spell = self.__spell_book.get(spell_name)
        if not spell:
            return f"{self.name}: spell '{spell_name}' not found"
        return spell.cast(self, target)

    def equip(self, artifact):
        if self.artifact is not None:
            print(f"Warning: {self.name} already has {self.artifact}, replacing it")
        self.artifact = artifact

    def __len__(self):
        return len(self.__spell_book)

    def __str__(self):
        return self.name

    def get_spells(self):
        return list(self.__spell_book.values())
