def insertion_sort(arr, visualizer, title="Сортировка вставками"):
    n = len(arr)
    steps = 0

    for i in range(1, n):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            visualizer.draw(arr, comparing=(j, j + 1),
                            sorted_indices=range(i),
                            title=title, step_count=steps)
            steps += 1

            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key
        # Один draw после вставки элемента на место
        visualizer.draw(arr, comparing=(),
                        sorted_indices=range(i + 1),
                        title=title, step_count=steps)

    visualizer.draw(arr, comparing=(),
                    sorted_indices=range(n),
                    title=f"{title} (Завершено)", step_count=steps)
    return steps
