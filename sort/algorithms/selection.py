def selection_sort(arr, visualizer, title="Сортировка выбором"):
    n = len(arr)
    steps = 0

    for i in range(n - 1):
        min_idx = i

        for j in range(i + 1, n):
            visualizer.draw(arr, comparing=(min_idx, j),
                            sorted_indices=range(i),
                            title=title, step_count=steps)
            steps += 1

            if arr[j] < arr[min_idx]:
                min_idx = j

        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            # Один draw после свапа, не дублируем
            visualizer.draw(arr, comparing=(),
                            sorted_indices=range(i + 1),
                            title=title, step_count=steps)
        else:
            visualizer.draw(arr, comparing=(),
                            sorted_indices=range(i + 1),
                            title=title, step_count=steps)

    visualizer.draw(arr, comparing=(),
                    sorted_indices=range(n),
                    title=f"{title} (Завершено)", step_count=steps)
    return steps
