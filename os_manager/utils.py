def format_bytes(n):
    if n < 1024:
        return f"{n} B"
    elif n < 1024 ** 2:
        return f"{n / 1024:.2f} KB"
    elif n < 1024 ** 3:
        return f"{n / (1024 ** 2):.2f} MB"
    elif n < 1024 ** 4:
        return f"{n / (1024 ** 3):.2f} GB"
    else:
        return f"{n / (1024 ** 4):.2f} TB"

def format_uptime(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{int(days)} д")
    if hours > 0:
        parts.append(f"{int(hours)} ч")
    if minutes > 0:
        parts.append(f"{int(minutes)} мин")
    if secs > 0 or not parts:
        parts.append(f"{int(secs)} с")
    
    return " ".join(parts)

def progress_bar(percent, width=20):
    filled = int(width * percent / 100)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {percent:.1f}%"

def print_table(headers, rows):
    if not rows:
        print("Нет данных для отображения")
        return
    
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in rows:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(min(max_width, 50))
    
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    
    print(separator)
    header_line = "|"
    for i, header in enumerate(headers):
        header_line += f" {str(header):<{col_widths[i]}} |"
    print(header_line)
    print(separator)
    
    for row in rows:
        line = "|"
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cell_str = str(cell) if cell is not None else ""
                if len(cell_str) > col_widths[i]:
                    cell_str = cell_str[:col_widths[i]-3] + "..."
                line += f" {cell_str:<{col_widths[i]}} |"
        print(line)
    
    print(separator)

def confirm(prompt):
    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            print("Пожалуйста, введите y или n")

if __name__ == "__main__":
    print("Тестирование format_bytes:")
    print(f"1023 байт -> {format_bytes(1023)}")
    print(f"1024 байт -> {format_bytes(1024)}")
    print(f"1500000 байт -> {format_bytes(1500000)}")
    print(f"2000000000 байт -> {format_bytes(2000000000)}")
    
    print("\nТестирование format_uptime:")
    print(f"3665 секунд -> {format_uptime(3665)}")
    print(f"90061 секунд -> {format_uptime(90061)}")
    
    print("\nТестирование progress_bar:")
    print(progress_bar(45, 20))
    print(progress_bar(78, 30))
    
    print("\nТестирование print_table:")
    headers = ["Имя", "Возраст", "Город"]
    rows = [["Анна", 25, "Москва"], ["Максим", 30, "Санкт-Петербург"], ["Елена", 28, "Новосибирск"]]
    print_table(headers, rows)
    
    print("\nТестирование confirm:")
    result = confirm("Тестовый вопрос")
    print(f"Результат: {result}")