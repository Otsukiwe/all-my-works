import psutil
import platform
import os
import signal
from datetime import datetime
from logger import get_logger
from utils import print_table, confirm, format_bytes

log = get_logger("process_manager")

def get_process_info(proc):
    try:
        info = proc.info
        mem_mb = info.get('memory_info', [0])[0] / (1024 * 1024) if info.get('memory_info') else 0
        create_time = info.get('create_time', 0)
        if create_time:
            start_time = datetime.fromtimestamp(create_time).strftime('%H:%M:%S')
        else:
            start_time = "N/A"
        
        return {
            'pid': info.get('pid', 0),
            'name': info.get('name', 'N/A')[:30],
            'status': info.get('status', 'N/A'),
            'cpu_percent': info.get('cpu_percent', 0),
            'memory_mb': mem_mb,
            'username': info.get('username', 'N/A')[:20],
            'start_time': start_time
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def list_processes(sort_by="cpu", filter_user=None, min_cpu=None, min_ram=None):
    log.info(f"Запрос списка процессов: sort_by={sort_by}, filter_user={filter_user}")
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info', 'username', 'create_time']):
        info = get_process_info(proc)
        if info:
            processes.append(info)
    
    if filter_user:
        processes = [p for p in processes if p['username'].lower() == filter_user.lower()]
    
    if min_cpu is not None:
        processes = [p for p in processes if p['cpu_percent'] >= min_cpu]
    
    if min_ram is not None:
        processes = [p for p in processes if p['memory_mb'] >= min_ram]
    
    sort_map = {
        "cpu": ('cpu_percent', True),
        "memory": ('memory_mb', True),
        "name": ('name', False),
        "pid": ('pid', False)
    }
    
    if sort_by in sort_map:
        key, reverse = sort_map[sort_by]
        processes.sort(key=lambda x: x[key], reverse=reverse)
    
    headers = ["PID", "Имя", "Статус", "CPU%", "RAM(MB)", "Пользователь", "Время старта"]
    rows = [[
        p['pid'], p['name'], p['status'],
        f"{p['cpu_percent']:.1f}", f"{p['memory_mb']:.1f}",
        p['username'], p['start_time']
    ] for p in processes[:50]]
    
    print_table(headers, rows)
    log.info(f"Отображено {len(rows)} процессов")
    return processes

def find_by_name(name):
    log.info(f"Поиск процессов по имени: {name}")
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_info', 'username', 'create_time']):
        try:
            proc_name = proc.info['name']
            if proc_name and name.lower() in proc_name.lower():
                info = get_process_info(proc)
                if info:
                    processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if processes:
        headers = ["PID", "Имя", "Статус", "CPU%", "RAM(MB)", "Пользователь"]
        rows = [[p['pid'], p['name'], p['status'], f"{p['cpu_percent']:.1f}", f"{p['memory_mb']:.1f}", p['username']] for p in processes]
        print_table(headers, rows)
    else:
        print(f"Процессы с именем '{name}' не найдены")
    
    return processes

def process_details(pid):
    log.info(f"Запрос деталей процесса PID={pid}")
    try:
        proc = psutil.Process(pid)
        
        print(f"\n{'='*60}")
        print(f"ДЕТАЛИ ПРОЦЕССА PID={pid}")
        print(f"{'='*60}")
        
        print(f"Имя: {proc.name()}")
        print(f"Статус: {proc.status()}")
        print(f"Пользователь: {proc.username()}")
        print(f"Исполняемый файл: {proc.exe()}")
        print(f"Рабочая директория: {proc.cwd()}")
        
        print(f"\nCPU и память:")
        print(f"  CPU %: {proc.cpu_percent(interval=0.1)}%")
        print(f"  Память RSS: {format_bytes(proc.memory_info().rss)}")
        print(f"  Память VMS: {format_bytes(proc.memory_info().vms)}")
        
        print(f"\nОткрытые файлы:")
        try:
            files = proc.open_files()
            if files:
                for f in files[:10]:
                    print(f"  {f.path}")
                if len(files) > 10:
                    print(f"  ... и еще {len(files)-10} файлов")
            else:
                print("  Нет открытых файлов")
        except psutil.AccessDenied:
            print("  Нет доступа")
        
        print(f"\nСетевые соединения:")
        try:
            connections = proc.connections()
            if connections:
                for conn in connections[:10]:
                    status = conn.status if hasattr(conn, 'status') else 'UNKNOWN'
                    print(f"  {conn.laddr} -> {conn.raddr} [{status}]")
                if len(connections) > 10:
                    print(f"  ... и еще {len(connections)-10} соединений")
            else:
                print("  Нет активных соединений")
        except psutil.AccessDenied:
            print("  Нет доступа")
        
        print(f"\nДочерние процессы:")
        try:
            children = proc.children()
            if children:
                for child in children:
                    print(f"  PID={child.pid}, Имя={child.name()}")
            else:
                print("  Нет дочерних процессов")
        except psutil.AccessDenied:
            print("  Нет доступа")
        
        print(f"\nПеременные окружения (первые 5):")
        try:
            env = proc.environ()
            for i, (key, value) in enumerate(list(env.items())[:5]):
                print(f"  {key}={value[:50]}")
            if len(env) > 5:
                print(f"  ... и еще {len(env)-5} переменных")
        except psutil.AccessDenied:
            print("  Нет доступа")
            
    except psutil.NoSuchProcess:
        print(f"Процесс с PID={pid} не существует")
        log.error(f"Процесс PID={pid} не найден")
    except psutil.AccessDenied:
        print(f"Нет доступа к процессу PID={pid}")
        log.error(f"Нет доступа к PID={pid}")
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка при получении деталей PID={pid}: {e}")

def kill_process(pid, force=False):
    current_pid = os.getpid()
    
    if pid == current_pid:
        print("Нельзя завершить саму программу!")
        log.warning(f"Попытка завершить собственную программу PID={pid}")
        return False
    
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        
        is_system = False
        try:
            if proc.username() in ['SYSTEM', 'root', 'Administrator'] or pid < 100:
                is_system = True
        except:
            pass
        
        if is_system:
            if not confirm(f"Внимание! Процесс {proc_name} (PID={pid}) является системным. Завершить?"):
                print("Операция отменена")
                return False
        
        if force:
            proc.kill()
            log.info(f"Принудительно завершён процесс PID={pid}, Имя={proc_name}")
            print(f"Процесс {proc_name} (PID={pid}) принудительно завершён")
        else:
            proc.terminate()
            proc.wait(timeout=3)
            log.info(f"Мягко завершён процесс PID={pid}, Имя={proc_name}")
            print(f"Процесс {proc_name} (PID={pid}) завершён")
        return True
        
    except psutil.NoSuchProcess:
        print(f"Процесс с PID={pid} не существует")
        log.error(f"Не удалось завершить: процесс PID={pid} не найден")
    except psutil.AccessDenied:
        print(f"Нет прав для завершения процесса PID={pid}")
        log.error(f"Нет прав для завершения PID={pid}")
    except Exception as e:
        print(f"Ошибка при завершении процесса: {e}")
        log.error(f"Ошибка при завершении PID={pid}: {e}")
    return False

def suspend_process(pid):
    try:
        proc = psutil.Process(pid)
        
        if platform.system() == "Windows":
            proc.suspend()
        else:
            proc.suspend()
        
        log.info(f"Приостановлен процесс PID={pid}, Имя={proc.name()}")
        print(f"Процесс {proc.name()} (PID={pid}) приостановлен")
        return True
    except psutil.NoSuchProcess:
        print(f"Процесс с PID={pid} не существует")
        log.error(f"Не удалось приостановить: процесс PID={pid} не найден")
    except psutil.AccessDenied:
        print(f"Нет прав для приостановки процесса PID={pid}")
        log.error(f"Нет прав для приостановки PID={pid}")
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка при приостановке PID={pid}: {e}")
    return False

def resume_process(pid):
    try:
        proc = psutil.Process(pid)
        
        if platform.system() == "Windows":
            proc.resume()
        else:
            proc.resume()
        
        log.info(f"Возобновлён процесс PID={pid}, Имя={proc.name()}")
        print(f"Процесс {proc.name()} (PID={pid}) возобновлён")
        return True
    except psutil.NoSuchProcess:
        print(f"Процесс с PID={pid} не существует")
        log.error(f"Не удалось возобновить: процесс PID={pid} не найден")
    except psutil.AccessDenied:
        print(f"Нет прав для возобновления процесса PID={pid}")
        log.error(f"Нет прав для возобновления PID={pid}")
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка при возобновлении PID={pid}: {e}")
    return False

def set_priority(pid, level):
    try:
        proc = psutil.Process(pid)
        
        if platform.system() == "Windows":
            priority_map = {
                "idle": psutil.IDLE_PRIORITY_CLASS,
                "below": psutil.BELOW_NORMAL_PRIORITY_CLASS,
                "normal": psutil.NORMAL_PRIORITY_CLASS,
                "above": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                "high": psutil.HIGH_PRIORITY_CLASS,
                "realtime": psutil.REALTIME_PRIORITY_CLASS
            }
            if level in priority_map:
                proc.nice(priority_map[level])
        else:
            nice_values = {
                "idle": 19,
                "below": 10,
                "normal": 0,
                "above": -5,
                "high": -10,
                "realtime": -20
            }
            if level in nice_values:
                proc.nice(nice_values[level])
        
        log.info(f"Изменён приоритет процесса PID={pid}, Имя={proc.name()}, уровень={level}")
        print(f"Приоритет процесса {proc.name()} (PID={pid}) изменён на {level}")
        return True
    except psutil.NoSuchProcess:
        print(f"Процесс с PID={pid} не существует")
        log.error(f"Не удалось изменить приоритет: процесс PID={pid} не найден")
    except psutil.AccessDenied:
        print(f"Нет прав для изменения приоритета процесса PID={pid}")
        log.error(f"Нет прав для изменения приоритета PID={pid}")
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка при изменении приоритета PID={pid}: {e}")
    return False

def run():
    log.info("Запуск менеджера процессов")
    
    while True:
        print("\n" + "="*50)
        print("МЕНЕДЖЕР ПРОЦЕССОВ")
        print("="*50)
        print("1. Список процессов")
        print("2. Поиск по имени")
        print("3. Детали процесса")
        print("4. Завершить процесс")
        print("5. Приостановить/возобновить процесс")
        print("6. Изменить приоритет")
        print("0. Назад")
        print("-"*50)
        
        choice = input("Выберите действие: ").strip()
        
        if choice == '0':
            log.info("Выход из менеджера процессов")
            break
        
        elif choice == '1':
            print("\nФильтры (оставьте пустым для пропуска):")
            filter_user = input("Пользователь: ").strip() or None
            min_cpu = input("Мин. CPU %: ").strip()
            min_cpu = float(min_cpu) if min_cpu else None
            min_ram = input("Мин. RAM MB: ").strip()
            min_ram = float(min_ram) if min_ram else None
            
            print("\nСортировка: cpu/memory/name/pid")
            sort_by = input("Сортировать по (cpu): ").strip() or "cpu"
            
            list_processes(sort_by, filter_user, min_cpu, min_ram)
        
        elif choice == '2':
            name = input("Введите имя процесса для поиска: ").strip()
            if name:
                find_by_name(name)
            else:
                print("Имя не может быть пустым")
        
        elif choice == '3':
            try:
                pid = int(input("Введите PID: ").strip())
                process_details(pid)
            except ValueError:
                print("Неверный PID")
        
        elif choice == '4':
            try:
                pid = int(input("Введите PID: ").strip())
                force = input("Принудительное завершение? (y/n): ").strip().lower() == 'y'
                kill_process(pid, force)
            except ValueError:
                print("Неверный PID")
        
        elif choice == '5':
            try:
                pid = int(input("Введите PID: ").strip())
                action = input("Приостановить (s) или возобновить (r)? ").strip().lower()
                if action == 's':
                    suspend_process(pid)
                elif action == 'r':
                    resume_process(pid)
                else:
                    print("Неверный выбор")
            except ValueError:
                print("Неверный PID")
        
        elif choice == '6':
            try:
                pid = int(input("Введите PID: ").strip())
                print("Уровни: idle, below, normal, above, high, realtime")
                level = input("Уровень приоритета (normal): ").strip() or "normal"
                set_priority(pid, level)
            except ValueError:
                print("Неверный PID")
        
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    run()