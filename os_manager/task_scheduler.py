import threading
import subprocess
import time
from datetime import datetime
import psutil
from logger import get_logger
from utils import print_table, confirm
import os

log = get_logger("task_scheduler")

tasks = {}
task_threads = {}
task_stop_events = {}
task_outputs = {}

def add_task(name, command, task_type, param):
    if not name or not command:
        print("Имя и команда не могут быть пустыми")
        return False
    
    if name in tasks:
        print(f"Задача с именем '{name}' уже существует")
        return False
    
    if task_type == "repeat" and param < 5:
        if not confirm(f"Интервал {param} сек меньше 5 сек. Продолжить?"):
            return False
    
    tasks[name] = {
        'name': name,
        'command': command,
        'type': task_type,
        'param': param,
        'status': 'ожидает',
        'last_run': None,
        'next_run': None,
        'error': None
    }
    
    task_stop_events[name] = threading.Event()
    
    if task_type == "once":
        schedule_once(name, param)
    elif task_type == "repeat":
        schedule_repeat(name, param)
    elif task_type == "condition":
        schedule_condition(name, param)
    
    log.info(f"Добавлена задача {name}: {command} (тип={task_type}, параметр={param})")
    print(f"Задача '{name}' добавлена")
    return True

def run_task(task_name):
    task = tasks[task_name]
    log.info(f"Запуск задачи {task_name}: {task['command']}")
    
    try:
        result = subprocess.run(
            task['command'],
            shell=True,
            capture_output=True,
            text=True,
            encoding='cp866' if os.name == 'nt' else 'utf-8',
            timeout=30
        )
        
        task_outputs[task_name] = {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if result.returncode == 0:
            task['status'] = 'завершена' if task['type'] == 'once' else 'выполнена'
            log.info(f"Задача {task_name} выполнена успешно")
        else:
            task['status'] = 'ошибка'
            task['error'] = result.stderr[:200]
            log.error(f"Задача {task_name} завершилась с кодом {result.returncode}: {result.stderr[:100]}")
            
        if task['type'] == 'once':
            task['status'] = 'завершена'
            if task_name in task_stop_events:
                task_stop_events[task_name].set()
        
        task['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    except subprocess.TimeoutExpired:
        task['status'] = 'таймаут'
        task['error'] = "Превышено время выполнения (30 сек)"
        log.error(f"Задача {task_name} превысила таймаут")
    except Exception as e:
        task['status'] = 'ошибка'
        task['error'] = str(e)
        log.error(f"Ошибка выполнения задачи {task_name}: {e}")

def schedule_once(name, delay):
    def once_worker():
        if task_stop_events[name].wait(delay):
            return
        
        tasks[name]['next_run'] = datetime.fromtimestamp(time.time() + delay).strftime("%Y-%m-%d %H:%M:%S")
        run_task(name)
    
    thread = threading.Thread(target=once_worker, daemon=True)
    task_threads[name] = thread
    thread.start()

def schedule_repeat(name, interval):
    def repeat_worker():
        while not task_stop_events[name].is_set():
            tasks[name]['next_run'] = datetime.fromtimestamp(time.time() + interval).strftime("%Y-%m-%d %H:%M:%S")
            run_task(name)
            
            for i in range(interval):
                if task_stop_events[name].is_set():
                    return
                time.sleep(1)
    
    thread = threading.Thread(target=repeat_worker, daemon=True)
    task_threads[name] = thread
    thread.start()

def schedule_condition(name, threshold):
    def condition_worker():
        while not task_stop_events[name].is_set():
            cpu = psutil.cpu_percent(interval=1)
            
            if cpu < threshold:
                tasks[name]['next_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                run_task(name)
                
                for i in range(60):
                    if task_stop_events[name].is_set():
                        return
                    time.sleep(1)
            else:
                time.sleep(10)
    
    thread = threading.Thread(target=condition_worker, daemon=True)
    task_threads[name] = thread
    thread.start()

def list_tasks():
    if not tasks:
        print("Нет запланированных задач")
        return
    
    rows = []
    for task in tasks.values():
        rows.append([
            task['name'],
            task['type'],
            task['command'][:40],
            task['status'],
            task['next_run'] or '-',
            task['last_run'] or '-'
        ])
    
    headers = ["Имя", "Тип", "Команда", "Статус", "Следующий запуск", "Последний запуск"]
    print_table(headers, rows)

def delete_task(name):
    if name not in tasks:
        print(f"Задача '{name}' не найдена")
        return False
    
    if name in task_stop_events:
        task_stop_events[name].set()
    
    if name in task_threads and task_threads[name].is_alive():
        task_threads[name].join(timeout=2)
    
    del tasks[name]
    if name in task_stop_events:
        del task_stop_events[name]
    if name in task_threads:
        del task_threads[name]
    if name in task_outputs:
        del task_outputs[name]
    
    log.info(f"Удалена задача {name}")
    print(f"Задача '{name}' удалена")
    return True

def show_task_output(name):
    if name not in tasks:
        print(f"Задача '{name}' не найдена")
        return
    
    if name not in task_outputs:
        print(f"Задача '{name}' ещё не выполнялась")
        return
    
    output = task_outputs[name]
    print("\n" + "="*60)
    print(f"ВЫВОД ЗАДАЧИ: {name}")
    print(f"Время выполнения: {output['time']}")
    print(f"Код возврата: {output['returncode']}")
    print("="*60)
    
    if output['stdout']:
        print("\nSTDOUT:")
        print(output['stdout'])
    
    if output['stderr']:
        print("\nSTDERR:")
        print(output['stderr'])

def stop_all_tasks():
    log.info("Остановка всех задач")
    for name in list(tasks.keys()):
        if name in task_stop_events:
            task_stop_events[name].set()
    
    for name, thread in task_threads.items():
        if thread.is_alive():
            thread.join(timeout=2)
    
    tasks.clear()
    task_stop_events.clear()
    task_threads.clear()
    task_outputs.clear()

def run():
    log.info("Запуск планировщика задач")
    
    while True:
        print("\n" + "="*50)
        print("ПЛАНИРОВЩИК ЗАДАЧ")
        print("="*50)
        print("1. Добавить задачу")
        print("2. Список задач")
        print("3. Показать вывод задачи")
        print("4. Удалить задачу")
        print("0. Назад")
        print("-"*50)
        
        choice = input("Выберите действие: ").strip()
        
        if choice == '0':
            log.info("Выход из планировщика задач")
            break
        
        elif choice == '1':
            name = input("Имя задачи: ").strip()
            command = input("Команда: ").strip()
            
            print("\nТипы задач:")
            print("1. once - однократная (через N сек)")
            print("2. repeat - периодическая (каждые N сек)")
            print("3. condition - по условию (CPU < N%)")
            type_choice = input("Выберите тип (1/2/3): ").strip()
            
            if type_choice == '1':
                task_type = "once"
                param = input("Задержка (сек): ").strip()
            elif type_choice == '2':
                task_type = "repeat"
                param = input("Интервал (сек): ").strip()
            elif type_choice == '3':
                task_type = "condition"
                param = input("Порог CPU %: ").strip()
            else:
                print("Неверный тип")
                continue
            
            if not param.isdigit():
                print("Параметр должен быть числом")
                continue
            
            add_task(name, command, task_type, int(param))
        
        elif choice == '2':
            list_tasks()
        
        elif choice == '3':
            name = input("Имя задачи: ").strip()
            show_task_output(name)
        
        elif choice == '4':
            name = input("Имя задачи: ").strip()
            delete_task(name)
        
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    run()