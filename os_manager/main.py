# main.py
import sys
import signal
import platform
import getpass
from logger import get_logger, show_logs

log = get_logger("main")

monitor_running = False
scheduler_running = False

def signal_handler(signum, frame):
    print("\n\nПолучен сигнал завершения...")
    log.info("Получен сигнал завершения")
    
    try:
        import resource_monitor
        resource_monitor.stop_monitor()
        resource_monitor.stop_alerts()
    except:
        pass
    
    try:
        import task_scheduler
        task_scheduler.stop_all_tasks()
    except:
        pass
    
    log.info("Программа завершена")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get_os_name():
    system = platform.system()
    if system == "Windows":
        return f"Windows {platform.release()}"
    elif system == "Linux":
        return f"Linux {platform.freedesktop_os_release().get('NAME', 'Unknown')}" if hasattr(platform, 'freedesktop_os_release') else "Linux"
    elif system == "Darwin":
        return "macOS"
    return system

def show_header():
    user = getpass.getuser()
    os_name = get_os_name()
    
    print("\n" + "╔" + "═"*48 + "╗")
    print(f"║{'OS Manager v1.0':^48}║")
    print(f"║{'Пользователь: ' + user:^48}║")
    print(f"║{'ОС: ' + os_name[:35]:^48}║")
    print("╚" + "═"*48 + "╝")

def show_main_menu():
    print("\n" + "="*50)
    print("1. Информация о системе")
    print("2. Менеджер процессов")
    print("3. Файловый менеджер")
    print("4. Мониторинг ресурсов")
    print("5. Планировщик задач")
    print("6. Просмотр логов")
    print("0. Выход")
    print("="*50)

def main():
    log.info("Программа запущена")
    
    modules = {
        1: None,
        2: None,
        3: None,
        4: None,
        5: None,
        6: None,
    }
    
    while True:
        show_header()
        show_main_menu()
        choice = input("Выберите пункт меню: ").strip()
        
        if choice == '0':
            log.info("Программа завершена пользователем")
            
            try:
                import resource_monitor
                resource_monitor.stop_monitor()
                resource_monitor.stop_alerts()
            except:
                pass
            
            try:
                import task_scheduler
                task_scheduler.stop_all_tasks()
            except:
                pass
            
            print("\nДо свидания!")
            break
        
        elif choice == '1':
            if modules[1] is None:
                import system_info
                modules[1] = system_info
            modules[1].run()
        
        elif choice == '2':
            if modules[2] is None:
                import process_manager
                modules[2] = process_manager
            modules[2].run()
        
        elif choice == '3':
            if modules[3] is None:
                import file_manager
                modules[3] = file_manager
            modules[3].run()
        
        elif choice == '4':
            if modules[4] is None:
                import resource_monitor
                modules[4] = resource_monitor
            modules[4].run()
        
        elif choice == '5':
            if modules[5] is None:
                import task_scheduler
                modules[5] = task_scheduler
            modules[5].run()
        
        elif choice == '6':
            level = input("Фильтр по уровню (DEBUG/INFO/WARNING/ERROR, Enter для всех): ").strip()
            show_logs(50, level if level else None)
        
        else:
            print("\nНеверный ввод. Пожалуйста, выберите пункт от 0 до 6.")
            log.warning(f"Неверный ввод в меню: {choice}")

if __name__ == "__main__":
    main()