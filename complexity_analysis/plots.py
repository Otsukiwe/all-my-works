import matplotlib.pyplot as plt
import numpy as np

def plot_linear(results):
    fig, ax = plt.subplots(figsize=(10, 6))
    for algo in ['constant', 'binary_search', 'linear_search', 'array_sum', 'merge_sort_random', 'bubble_sort_random']:
        if algo in results:
            ns, ts = zip(*results[algo])
            ax.plot(ns, ts, marker='o', label=algo)
    ax.set_xlabel('Размер входа n')
    ax.set_ylabel('Время (сек)')
    ax.set_title('Время выполнения алгоритмов (линейный масштаб)')
    ax.legend()
    ax.grid(True)
    fig.savefig('plot1_linear.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

def plot_loglog(results):
    fig, ax = plt.subplots(figsize=(10, 6))
    for algo in ['linear_search', 'array_sum', 'merge_sort_random', 'bubble_sort_random']:
        if algo in results:
            ns, ts = zip(*results[algo])
            ax.loglog(ns, ts, marker='o', label=algo)
    ax.set_xlabel('log(n)')
    ax.set_ylabel('log(время)')
    ax.set_title('Время выполнения (log-log масштаб)')
    ax.legend()
    ax.grid(True, which='both')
    fig.savefig('plot2_loglog.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

def plot_cases(results):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    for case, label in [('bubble_sort_random', 'Случайный'), ('bubble_sort_sorted', 'Отсортированный'), ('bubble_sort_reverse', 'Обратный')]:
        ns, ts = zip(*results[case])
        ax1.plot(ns, ts, marker='o', label=label)
    ax1.set_title('Bubble Sort: лучший/средний/худший случай')
    ax1.set_xlabel('n'); ax1.set_ylabel('Время (сек)')
    ax1.legend(); ax1.grid(True)

    for case, label in [('merge_sort_random', 'Случайный'), ('merge_sort_sorted', 'Отсортированный'), ('merge_sort_reverse', 'Обратный')]:
        ns, ts = zip(*results[case])
        ax2.plot(ns, ts, marker='o', label=label)
    ax2.set_title('Merge Sort: лучший/средний/худший случай')
    ax2.set_xlabel('n'); ax2.set_ylabel('Время (сек)')
    ax2.legend(); ax2.grid(True)

    fig.savefig('plot3_cases.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

def plot_heatmap(results):
    data = results['matrix_multiply']
    ns = [d[0] for d in data]
    ts = [d[1] for d in data]
    fig, ax = plt.subplots(figsize=(8, 5))
    matrix = np.array(ts).reshape(1, -1)
    im = ax.imshow(matrix, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(ns)))
    ax.set_xticklabels(ns)
    ax.set_yticks([])
    ax.set_xlabel('Размер матрицы n')
    ax.set_title('Тепловая карта: время перемножения матриц')
    plt.colorbar(im, ax=ax, label='Время (сек)')
    fig.savefig('plot4_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

def plot_fib(results):
    fig, ax = plt.subplots(figsize=(8, 5))
    ns, ts = zip(*results['fib'])
    ax.semilogy(ns, ts, marker='o', color='red', label='fib_recursive')
    ax.set_xlabel('n')
    ax.set_ylabel('Время (сек, log)')
    ax.set_title('Рекурсивный Фибоначчи O(2^n) — полулогарифмический график')
    ax.legend(); ax.grid(True)
    fig.savefig('plot5_fib.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

def fit_exponent(results, algo):
    data = [(n, t) for n, t in results[algo] if t > 0 and n > 0]
    ns = np.array([d[0] for d in data], dtype=float)
    ts = np.array([d[1] for d in data], dtype=float)
    log_n = np.log(ns)
    log_t = np.log(ts)
    k, _ = np.polyfit(log_n, log_t, 1)
    return k

def make_all_plots(results):
    plot_linear(results)
    plot_loglog(results)
    plot_cases(results)
    plot_heatmap(results)
    plot_fib(results)
