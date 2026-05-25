# Архитектура системы «Кодекс Нитей»

## Классы системы

| Класс | Тип | Принцип ООП | Файл |
|---|---|---|---|
| Thread | Конкретный | Инкапсуляция | threads.py |
| EnergyThread | Конкретный (наследник) | Наследование | threads.py |
| FormThread | Конкретный (наследник) | Наследование | threads.py |
| TimeThread | Конкретный (наследник) | Наследование | threads.py |
| Spell | Абстрактный | Абстракция | spells.py |
| WeaveSpell | Конкретный | Наследование, Полиморфизм | spells.py |
| CutSpell | Конкретный | Наследование, Полиморфизм | spells.py |
| BindSpell | Конкретный | Наследование, Полиморфизм | spells.py |
| LegendaryWeaveSpell | Конкретный | Наследование | spells.py |
| CombinedSpell | Конкретный (Composite) | Полиморфизм | spells.py |
| Artifact | Абстрактный | Абстракция | artifacts.py |
| CrystalCore | Конкретный | Наследование | artifacts.py |
| RuneMatrix | Конкретный | Наследование | artifacts.py |
| Caster | Конкретный | Инкапсуляция | caster.py |
| ArcaneInterface | Protocol | Абстракция (duck typing) | caster.py |

## Принципы ООП

**Инкапсуляция** — Thread скрывает __frequency, __stability, __name за @property с валидацией. Caster скрывает __spell_book.

**Наследование** — EnergyThread, FormThread, TimeThread наследуют Thread. WeaveSpell, CutSpell, BindSpell наследуют Spell. LegendaryWeaveSpell наследует WeaveSpell.

**Полиморфизм** — метод cast() вызывается единообразно для всех заклинаний. Перегрузка операторов + и > для Thread и Spell.

**Абстракция** — Spell(ABC) и Artifact(ABC) скрывают детали реализации. ArcaneInterface (Protocol) описывает интерфейс без наследования.

## Иерархия

```
Thread
├── EnergyThread
├── FormThread
└── TimeThread

Spell (ABC)
├── WeaveSpell
│   └── LegendaryWeaveSpell
├── CutSpell
├── BindSpell
└── CombinedSpell

Artifact (ABC)
├── CrystalCore
└── RuneMatrix
```
