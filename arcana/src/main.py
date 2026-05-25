import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from threads import EnergyThread, FormThread, TimeThread
from spells import WeaveSpell, CutSpell, BindSpell, LegendaryWeaveSpell, CombinedSpell, Rarity
from artifacts import CrystalCore, RuneMatrix
from caster import Caster


def execute_all(spells, caster, target):
    results = []
    for spell in spells:
        results.append(spell.cast(caster, target))
    return results


print("=== КОДЕКС НИТЕЙ — ДЕМОНСТРАЦИЯ ===\n")

energy_thread = EnergyThread("Нить Энергии", 500.0, 0.9, power=2.0)
form_thread = FormThread("Нить Формы", 300.0, 0.7, shape="сфера")
time_thread = TimeThread("Нить Времени", 200.0, 0.5, epoch=3)

print("--- Нити ---")
print(energy_thread)
print(form_thread)
print(time_thread)

combined = energy_thread + form_thread
print(f"Объединённая нить: {combined}\n")

print("--- Резонанс ---")
print(f"energy + form: {energy_thread.resonate(form_thread):.2f}")
print(f"form + time:   {form_thread.resonate(time_thread):.2f}\n")

varn = Caster("Архимаг Варн", energy=200)
sel = Caster("Ученица Сел", energy=40)

varn_artifact = RuneMatrix(capacity=5)
sel_artifact = CrystalCore()

varn.equip(varn_artifact)
sel.equip(sel_artifact)

varn_artifact.store(energy_thread)
varn_artifact.store(form_thread)

print("--- Замена артефакта (предупреждение) ---")
varn.equip(CrystalCore())
varn.equip(varn_artifact)
print()

lws = LegendaryWeaveSpell("Абсолютное Плетение", cost=30)
ws = WeaveSpell("Простое Плетение", cost=10)
cs = CutSpell("Разрыв", cost=8, severity=0.3)
bs = BindSpell("Оковы", cost=15, duration=5)
combined_spell = CombinedSpell("Двойной Удар", [ws, cs])

varn.learn(lws)
varn.learn(ws)
sel.learn(cs)
sel.learn(bs)
sel.learn(ws)

print("--- Дуэль ---")
print(varn.cast("Абсолютное Плетение", "Сел"))
print(varn.cast("Простое Плетение", "Сел"))
print(sel.cast("Разрыв", "Варн"))
print(sel.cast("Оковы", "Варн"))
print()

print("--- Полиморфизм: execute_all ---")
mixed_spells = [ws, cs, bs, lws, combined_spell]
for result in execute_all(mixed_spells, varn, "Сел"):
    print(result)
print()

print("--- Сравнение заклинаний (перегрузка >) ---")
print(f"lws > ws: {lws > ws}")
print(f"ws > lws: {ws > lws}")
print()

print("--- Итоговый отчёт ---")
for caster in [varn, sel]:
    print(f"Нитяр: {caster.name}")
    print(f"  Энергия: {caster.energy}")
    print(f"  Заклинаний в книге: {len(caster)}")
    print(f"  Артефакт: {caster.artifact}")
