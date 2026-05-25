import matplotlib.pyplot as plt
import numpy as np

class StatsCollector:
    def __init__(self, n):
        self.n = n
        self.results = {}
    
    def add_result(self, algorithm_name, steps):
        self.results[algorithm_name] = steps
    
    def display_results(self):
        print("\n" + "="*50)
        print(f"Сравнение алгоритмов (N = {self.n})")
        print("="*50)
        print(f"{'Алгоритм':<20} {'Шагов (сравнений)':<20}")
        print("-"*50)
        
        for name, steps in self.results.items():
            print(f"{name:<20} {steps:<20}")
        
        print("="*50)
        
        if self.results:
            winner = min(self.results, key=self.results.get)
            print(f"Победитель по шагам: {winner}")
            print("="*50)
    
    def plot_comparison(self):
        if len(self.results) < 2:
            print("Недостаточно данных для сравнения")
            return
        
        algorithms = list(self.results.keys())
        steps = list(self.results.values())
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(algorithms, steps, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        
        for bar, step in zip(bars, steps):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{step}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.xlabel('Алгоритм сортировки', fontsize=12)
        plt.ylabel('Количество сравнений', fontsize=12)
        plt.title(f'Сравнение эффективности алгоритмов (N = {self.n})', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        
        text = f"Теоретическая сложность всех алгоритмов: O(n²) = {self.n**2:,}"
        plt.figtext(0.5, 0.02, text, ha='center', fontsize=10, 
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.show()