def bubble_sort(arr, visualizer, title="Сортировка пузырьком"):
    n = len(arr)
    steps = 0
    sorted_from = n  # граница отсортированной части (справа)

    for i in range(n):
        swapped = False
        sorted_from = n - i

        for j in range(0, sorted_from - 1):
            # Один draw вместо двух: рисуем ДО сравнения, меняем если нужно
            visualizer.draw(arr, comparing=(j, j + 1),
                            sorted_indices=range(sorted_from, n),
                            title=title, step_count=steps)
            steps += 1

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        if not swapped:
            break

    visualizer.draw(arr, comparing=(),
                    sorted_indices=range(n),
                    title=f"{title} (Завершено)", step_count=steps)
    return steps
