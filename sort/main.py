import random
import copy
import matplotlib.pyplot as plt
from algorithms.bubble import bubble_sort
from algorithms.selection import selection_sort
from algorithms.insertion import insertion_sort
from visualizer import Visualizer
from stats import StatsCollector

def get_valid_n():
    while True:
        try:
            n = int(input("Введите количество элементов (2-2000): "))
            if 2 <= n <= 2000:
                return n
            else:
                print("Ошибка: N должно быть от 2 до 2000")
        except ValueError:
            print("Ошибка: Введите целое число")

def get_algorithm_choice():
    print("\nВыберите алгоритм:")
    print("1 - Сортировка пузырьком")
    print("2 - Сортировка выбором")
    print("3 - Сортировка вставками")
    print("4 - Запустить все алгоритмы")
    
    while True:
        try:
            choice = int(input("Ваш выбор (1-4): "))
            if 1 <= choice <= 4:
                return choice
            else:
                print("Ошибка: Введите число от 1 до 4")
        except ValueError:
            print("Ошибка: Введите целое число")

def main():
    n = get_valid_n()
    choice = get_algorithm_choice()
    
    random.seed(42)
    original_array = [random.randint(1, 100) for _ in range(n)]
    
    algorithms = {
        1: ("Пузырёк", bubble_sort),
        2: ("Выбор", selection_sort),
        3: ("Вставки", insertion_sort)
    }
    
    stats = StatsCollector(n)
    
    if choice == 4:
        for algo_id, (name, algo_func) in algorithms.items():
            print(f"\nЗапуск {name}...")
            visualizer = Visualizer(delay=0.00000000001)
            test_array = copy.deepcopy(original_array)
            steps = algo_func(test_array, visualizer, name)
            stats.add_result(name, steps)
            visualizer.close()
            print(f"{name} завершён. Нажмите Enter для следующего алгоритма...")
            input()
            plt.close('all')
        
        stats.display_results()
        stats.plot_comparison()
    else:
        name, algo_func = algorithms[choice]
        visualizer = Visualizer(delay=0)
        test_array = copy.deepcopy(original_array)
        steps = algo_func(test_array, visualizer, name)
        stats.add_result(name, steps)
        stats.display_results()
        visualizer.close()
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()