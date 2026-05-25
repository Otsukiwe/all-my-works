# resource_monitor.py (исправленная версия)
import threading
import time
import csv
import os
from datetime import datetime
import psutil
from logger import get_logger
from utils import progress_bar, format_bytes, print_table

log = get_logger("resource_monitor")

stop_event = threading.Event()
monitor_thread = None

last_net_stats = None
last_net_time = None
alert_last_triggered = {}
alert_cpu_threshold = None
alert_ram_threshold = None
alert_stop_event = threading.Event()
alert_thread = None
alert_running = False

def get_net_speed():
    global last_net_stats, last_net_time
    
    net_stats = psutil.net_io_counters()
    current_time = time.time()
    
    if last_net_stats is None:
        last_net_stats = net_stats
        last_net_time = current_time
        return 0, 0
    
    sent_speed = (net_stats.bytes_sent - last_net_stats.bytes_sent) / (current_time - last_net_time) / 1024
    recv_speed = (net_stats.bytes_recv - last_net_stats.bytes_recv) / (current_time - last_net_time) / 1024
    
    last_net_stats = net_stats
    last_net_time = current_time
    
    return sent_speed, recv_speed

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor_loop(interval):
    log.info(f"Запуск мониторинга с интервалом {interval} сек")
    
    while not stop_event.is_set():
        try:
            clear_screen()
            
            print("="*60)
            print("МОНИТОРИНГ РЕСУРСОВ СИСТЕМЫ")
            print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"\nCPU ЗАГРУЗКА:")
            print(progress_bar(cpu_percent, 40))
            print(f"Частота: {psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else "")
            
            mem = psutil.virtual_memory()
            print(f"\nОПЕРАТИВНАЯ ПАМЯТЬ:")
            print(f"Использовано: {format_bytes(mem.used)} из {format_bytes(mem.total)}")
            print(progress_bar(mem.percent, 40))
            
            swap = psutil.swap_memory()
            print(f"\nSWAP ПАМЯТЬ:")
            print(f"Использовано: {format_bytes(swap.used)} из {format_bytes(swap.total)}")
            print(progress_bar(swap.percent, 40))
            
            print(f"\nДИСКИ:")
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    print(f"{partition.mountpoint[:15]:15} {progress_bar(usage.percent, 25)}")
                except:
                    pass
            
            sent, recv = get_net_speed()
            print(f"\nСЕТЬ:")
            print(f"Отправлено: {sent:.2f} KB/s | Получено: {recv:.2f} KB/s")
            
            processes = len(psutil.pids())
            print(f"\nПРОЦЕССЫ: {processes}")
            
            print(f"\nТОП-5 ПО CPU:")
            cpu_top = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] > 0:
                        cpu_top.append((info['pid'], info['name'], info['cpu_percent']))
                except:
                    continue
            cpu_top.sort(key=lambda x: x[2], reverse=True)
            for pid, name, cpu in cpu_top[:5]:
                print(f"  PID {pid:6} {name[:20]:20} {cpu:6.1f}%")
            
            print(f"\nТОП-5 ПО RAM:")
            ram_top = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    info = proc.info
                    mem_mb = info['memory_info'].rss / 1024 / 1024 if info['memory_info'] else 0
                    if mem_mb > 0:
                        ram_top.append((info['pid'], info['name'], mem_mb))
                except:
                    continue
            ram_top.sort(key=lambda x: x[2], reverse=True)
            for pid, name, mem in ram_top[:5]:
                print(f"  PID {pid:6} {name[:20]:20} {mem:8.1f} MB")
            
            print("\n" + "="*60)
            print("Нажмите 'q' + Enter для остановки...")
            
        except Exception as e:
            log.error(f"Ошибка в мониторинге: {e}")
        
        stop_event.wait(interval)

def start_monitor(interval=2):
    global monitor_thread, stop_event
    
    if monitor_thread and monitor_thread.is_alive():
        print("Мониторинг уже запущен")
        return
    
    stop_event.clear()
    monitor_thread = threading.Thread(target=monitor_loop, args=(interval,), daemon=True)
    monitor_thread.start()
    
    while True:
        user_input = input()
        if user_input.lower() == 'q':
            stop_monitor()
            break

def stop_monitor():
    global monitor_thread
    
    if monitor_thread and monitor_thread.is_alive():
        stop_event.set()
        monitor_thread.join(timeout=2)
        log.info("Мониторинг остановлен")
        print("\nМониторинг остановлен")

def record_metrics(filename, interval=2):
    log.info(f"Начало записи метрик в {filename}")
    
    data = []
    stop_recording = threading.Event()
    
    def record_loop():
        last_net = psutil.net_io_counters()
        last_time = time.time()
        
        while not stop_recording.is_set():
            try:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                swap = psutil.swap_memory().percent
                
                net_stats = psutil.net_io_counters()
                current_time = time.time()
                sent_kb = (net_stats.bytes_sent - last_net.bytes_sent) / (current_time - last_time) / 1024
                recv_kb = (net_stats.bytes_recv - last_net.bytes_recv) / (current_time - last_time) / 1024
                last_net = net_stats
                last_time = current_time
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data.append([timestamp, cpu, mem, swap, sent_kb, recv_kb])
                
            except Exception as e:
                log.error(f"Ошибка записи метрик: {e}")
            
            stop_recording.wait(interval)
    
    record_thread = threading.Thread(target=record_loop, daemon=True)
    record_thread.start()
    
    input("Запись метрик... Нажмите Enter для остановки\n")
    stop_recording.set()
    record_thread.join(timeout=2)
    
    if not data:
        print("Нет данных для сохранения")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['datetime', 'cpu', 'ram', 'swap', 'net_sent_kb', 'net_recv_kb'])
        writer.writerows(data)
    
    print(f"\nДанные сохранены в {filename}")
    
    cpu_vals = [row[1] for row in data]
    ram_vals = [row[2] for row in data]
    swap_vals = [row[3] for row in data]
    
    print("\n" + "="*50)
    print("СТАТИСТИКА ЗАПИСИ")
    print("="*50)
    print(f"Всего записей: {len(data)}")
    print(f"\nCPU: среднее={sum(cpu_vals)/len(cpu_vals):.1f}%, мин={min(cpu_vals):.1f}%, макс={max(cpu_vals):.1f}%")
    print(f"RAM: среднее={sum(ram_vals)/len(ram_vals):.1f}%, мин={min(ram_vals):.1f}%, макс={max(ram_vals):.1f}%")
    print(f"Swap: среднее={sum(swap_vals)/len(swap_vals):.1f}%, мин={min(swap_vals):.1f}%, макс={max(swap_vals):.1f}%")
    
    log.info(f"Запись метрик завершена, сохранено {len(data)} записей")

def alert_loop():
    global alert_last_triggered, alert_running
    
    log.info("Поток оповещений запущен")
    
    while alert_running and not alert_stop_event.is_set():
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            
            current_time = time.time()
            
            if alert_cpu_threshold and cpu > alert_cpu_threshold:
                last_time = alert_last_triggered.get('cpu', 0)
                if current_time - last_time > 60:
                    msg = f"⚠ ПРЕВЫШЕНИЕ CPU: {cpu:.1f}% > {alert_cpu_threshold}%"
                    print(f"\n{msg}")
                    log.warning(msg)
                    alert_last_triggered['cpu'] = current_time
            
            if alert_ram_threshold and ram > alert_ram_threshold:
                last_time = alert_last_triggered.get('ram', 0)
                if current_time - last_time > 60:
                    msg = f"⚠ ПРЕВЫШЕНИЕ RAM: {ram:.1f}% > {alert_ram_threshold}%"
                    print(f"\n{msg}")
                    log.warning(msg)
                    alert_last_triggered['ram'] = current_time
            
        except Exception as e:
            log.error(f"Ошибка в потоке оповещений: {e}")
        
        alert_stop_event.wait(5)

def set_alert(cpu_threshold=None, ram_threshold=None):
    global alert_cpu_threshold, alert_ram_threshold, alert_thread, alert_stop_event, alert_running
    
    alert_cpu_threshold = cpu_threshold
    alert_ram_threshold = ram_threshold
    
    if alert_thread and alert_thread.is_alive():
        alert_running = False
        alert_stop_event.set()
        alert_thread.join(timeout=2)
    
    if cpu_threshold is not None or ram_threshold is not None:
        alert_running = True
        alert_stop_event.clear()
        alert_last_triggered.clear()
        alert_thread = threading.Thread(target=alert_loop, daemon=True)
        alert_thread.start()
        print(f"Оповещения установлены: CPU>{cpu_threshold}%, RAM>{ram_threshold}%")
        log.info(f"Установлены оповещения CPU>{cpu_threshold}%, RAM>{ram_threshold}%")
    else:
        print("Оповещения отключены")
        log.info("Оповещения отключены")

def stop_alerts():
    global alert_running, alert_thread, alert_stop_event
    
    if alert_thread and alert_thread.is_alive():
        alert_running = False
        alert_stop_event.set()
        alert_thread.join(timeout=2)
        print("Оповещения остановлены")
        log.info("Оповещения остановлены")

def run():
    global alert_running
    
    log.info("Запуск мониторинга ресурсов")
    alert_running = False
    
    while True:
        print("\n" + "="*50)
        print("МОНИТОРИНГ РЕСУРСОВ")
        print("="*50)
        print("1. Живой мониторинг")
        print("2. Запись метрик в CSV")
        print("3. Установить оповещения")
        print("4. Остановить оповещения")
        print("0. Назад")
        print("-"*50)
        
        choice = input("Выберите действие: ").strip()
        
        if choice == '0':
            stop_monitor()
            stop_alerts()
            log.info("Выход из мониторинга ресурсов")
            break
        
        elif choice == '1':
            interval = input("Интервал обновления (сек, по умолч. 2): ").strip()
            interval = int(interval) if interval.isdigit() else 2
            start_monitor(interval)
        
        elif choice == '2':
            filename = input("Имя CSV файла (metrics.csv): ").strip()
            if not filename:
                filename = "metrics.csv"
            if not filename.endswith('.csv'):
                filename += '.csv'
            interval = input("Интервал записи (сек, по умолч. 2): ").strip()
            interval = int(interval) if interval.isdigit() else 2
            record_metrics(filename, interval)
        
        elif choice == '3':
            cpu_thresh = input("Порог CPU % (Enter для пропуска): ").strip()
            ram_thresh = input("Порог RAM % (Enter для пропуска): ").strip()
            cpu_thresh = int(cpu_thresh) if cpu_thresh else None
            ram_thresh = int(ram_thresh) if ram_thresh else None
            set_alert(cpu_thresh, ram_thresh)
            
            input("\nНажмите Enter для продолжения...")
        
        elif choice == '4':
            stop_alerts()
            input("\nНажмите Enter для продолжения...")
        
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    run()