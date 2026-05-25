import matplotlib
matplotlib.use('TkAgg')  
import matplotlib.pyplot as plt
import numpy as np

class Visualizer:
    def __init__(self, delay=0.0001):
        self.delay = delay
        self._closed = False

        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(15, 8))
        self.fig.canvas.manager.set_window_title("Визуальная сортировка")

       
        self._colors = []
        self.bars = None
        self._info_text = None
        self._bar_texts = []
        self._n = 0

    def _ensure_init(self, array):
        n = len(array)
        if self.bars is None or n != self._n:
            self.ax.cla()
            self._n = n
            self._colors = ['steelblue'] * n

            self.bars = self.ax.bar(range(n), array,
                                    color=self._colors, alpha=0.8, edgecolor='black',
                                    linewidth=0.5)
            self.ax.set_xlabel('Индекс', fontsize=11)
            self.ax.set_ylabel('Значение', fontsize=11)
            self.ax.grid(True, alpha=0.3, axis='y', linewidth=0.5)
            self.ax.set_xlim(-0.5, n - 0.5)

           
            self._bar_texts = []
            if n <= 30:
                for bar, val in zip(self.bars, array):
                    t = self.ax.text(bar.get_x() + bar.get_width() / 2.,
                                     bar.get_height() + 1, str(val),
                                     ha='center', va='bottom', fontsize=8)
                    self._bar_texts.append(t)

            
            self._info_text = self.ax.text(
                0.02, 0.98, '', transform=self.ax.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            )

        return n

    def draw(self, array, comparing=(), sorted_indices=(), title='', step_count=0):
        if self._closed or not plt.fignum_exists(self.fig.number):
            self._closed = True
            return

        n = self._ensure_init(array)
        max_val = 0

        
        comparing_set = set(comparing)
        sorted_set = set(sorted_indices)

        for i, bar in enumerate(self.bars):
            h = array[i]
            if h > max_val:
                max_val = h
            bar.set_height(h)

            if i in comparing_set:
                bar.set_color('red')
            elif i in sorted_set:
                bar.set_color('lightgreen')
            else:
                bar.set_color('steelblue')

      
        if self._bar_texts:
            for t, bar, val in zip(self._bar_texts, self.bars, array):
                t.set_position((bar.get_x() + bar.get_width() / 2., val + 1))
                t.set_text(str(val))

        self.ax.set_ylim(0, max_val + 10)
        self.ax.set_title(f'{title} | Шагов: {step_count}', fontsize=13, fontweight='bold')
        self._info_text.set_text(f'Размер: {n}\nСравнений: {step_count}')

        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

        if self.delay > 0:
            plt.pause(self.delay)

    def close(self):
        if not self._closed and plt.fignum_exists(self.fig.number):
            plt.close(self.fig)
        self._closed = True
