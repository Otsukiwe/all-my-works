import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from benchmark import run_benchmarks
from plots import make_all_plots, fit_exponent

print("Запуск замеров...")
results = run_benchmarks()
print("Построение графиков...")
make_all_plots(results)

print("\nИтоговая таблица:")
print(f"{'Алгоритм':<25} {'Теория':>8} {'Эмпирика':>10} {'Отклонение':>12} {'Оценка':>8}")
print("-" * 70)

checks = [
    ('linear_search',       1.0),
    ('array_sum',           1.0),
    ('merge_sort_random',   1.0),
    ('bubble_sort_random',  2.0),
    ('matrix_multiply',     3.0),
]

for algo, theory in checks:
    k = fit_exponent(results, algo)
    dev = abs(k - theory)
    grade = 'хорошо' if dev < 0.15 else 'требует проверки'
    print(f"{algo:<25} {theory:>8.1f} {k:>10.2f} {dev:>12.2f} {grade:>8}")

print("\nГотово! Все графики и results.csv сохранены.")
