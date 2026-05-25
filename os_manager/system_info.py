import platform
import psutil
import socket
import urllib.request
import urllib.error
import time
from datetime import datetime
from logger import get_logger
from utils import format_bytes, format_uptime, progress_bar, print_table

log = get_logger("system_info")

def get_os_info():
    print("\n" + "="*60)
    print("ОПЕРАЦИОННАЯ СИСТЕМА")
    print("="*60)
    
    system = platform.system()
    release = platform.release()
    version = platform.version()
    kernel = platform.version()
    
    print(f"Название ОС: {system} {release}")
    print(f"Версия: {version}")
    print(f"Версия ядра: {kernel}")
    print(f"Разрядность: {platform.machine()}")
    print(f"Имя компьютера: {socket.gethostname()}")
    print(f"Текущий пользователь: {psutil.users()[0].name if psutil.users() else 'Неизвестно'}")
    
    boot_time = psutil.boot_time()
    boot_datetime = datetime.fromtimestamp(boot_time)
    uptime_seconds = time.time() - boot_time
    
    print(f"Время последней загрузки: {boot_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Аптайм: {format_uptime(uptime_seconds)}")

def get_cpu_info():
    print("\n" + "="*60)
    print("ПРОЦЕССОР")
    print("="*60)
    
    cpu_model = "Неизвестно"
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu_model = winreg.QueryValueEx(key, "ProcessorNameString")[0]
            winreg.CloseKey(key)
        else:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        cpu_model = line.split(":")[1].strip()
                        break
    except:
        cpu_model = platform.processor()
    
    print(f"Модель CPU: {cpu_model}")
    print(f"Физические ядра: {psutil.cpu_count(logical=False)}")
    print(f"Логические потоки: {psutil.cpu_count(logical=True)}")
    
    freq = psutil.cpu_freq()
    if freq:
        print(f"Текущая частота: {freq.current:.0f} MHz")
        print(f"Максимальная частота: {freq.max:.0f} MHz")
    
    print("\nОбщая загрузка CPU (1 сек):")
    cpu_percent = psutil.cpu_percent(interval=1)
    print(progress_bar(cpu_percent))
    
    print("\nЗагрузка каждого ядра:")
    per_cpu = psutil.cpu_percent(interval=1, percpu=True)
    for i, perc in enumerate(per_cpu):
        print(f"Ядро {i}: {progress_bar(perc, width=30)}")

def get_memory_info():
    print("\n" + "="*60)
    print("ПАМЯТЬ")
    print("="*60)
    
    mem = psutil.virtual_memory()
    print("ОПЕРАТИВНАЯ ПАМЯТЬ:")
    print(f"Общий объём: {format_bytes(mem.total)}")
    print(f"Используется: {format_bytes(mem.used)}")
    print(f"Свободно: {format_bytes(mem.free)}")
    print(progress_bar(mem.percent))
    
    swap = psutil.swap_memory()
    print("\nSWAP ПАМЯТЬ:")
    print(f"Общий объём: {format_bytes(swap.total)}")
    print(f"Используется: {format_bytes(swap.used)}")
    print(f"Свободно: {format_bytes(swap.free)}")
    print(progress_bar(swap.percent))

def get_network_info():
    print("\n" + "="*60)
    print("СЕТЬ")
    print("="*60)
    
    print("Сетевые интерфейсы:")
    interfaces = []
    for iface, addrs in psutil.net_if_addrs().items():
        ipv4 = ""
        ipv6 = ""
        mac = ""
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ipv4 = addr.address
            elif addr.family == socket.AF_INET6:
                ipv6 = addr.address
            elif addr.family == psutil.AF_LINK:
                mac = addr.address
        interfaces.append([iface, ipv4, ipv6[:30] if ipv6 else "", mac])
    
    print_table(["Интерфейс", "IPv4", "IPv6", "MAC"], interfaces)
    
    print("\nВнешний IP-адрес:")
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as response:
            external_ip = response.read().decode('utf-8')
            print(f"Внешний IP: {external_ip}")
            log.info(f"Получен внешний IP: {external_ip}")
    except urllib.error.URLError:
        print("Не удалось получить внешний IP (нет интернета)")
        log.warning("Не удалось получить внешний IP")
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка при получении внешнего IP: {e}")

def run():
    log.info("Запуск подсистемы информации о системе")
    try:
        get_os_info()
        get_cpu_info()
        get_memory_info()
        get_network_info()
        log.info("Подсистема информации о системе завершена успешно")
    except Exception as e:
        log.error(f"Ошибка в подсистеме информации о системе: {e}")
        print(f"\nОшибка: {e}")

if __name__ == "__main__":
    run()