import os
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime
from logger import get_logger
from utils import format_bytes, print_table, confirm

log = get_logger("file_manager")

current_dir = os.getcwd()

def list_dir():
    global current_dir
    log.info(f"Просмотр содержимого: {current_dir}")
    
    try:
        items = []
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            try:
                stat = os.stat(item_path)
                if os.path.isdir(item_path):
                    item_type = "DIR"
                    size = 0
                else:
                    item_type = "FILE"
                    size = stat.st_size
                
                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                perms = ""
                perms += "r" if os.access(item_path, os.R_OK) else "-"
                perms += "w" if os.access(item_path, os.W_OK) else "-"
                perms += "x" if os.access(item_path, os.X_OK) else "-"
                
                items.append([item, item_type, format_bytes(size), mod_time, perms])
            except:
                items.append([item, "?", "?", "?", "?"])
        
        headers = ["Имя", "Тип", "Размер", "Изменён", "Права"]
        print_table(headers, items)
        print(f"\nТекущая директория: {current_dir}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка при просмотре {current_dir}: {e}")

def change_dir(path):
    global current_dir
    log.info(f"Переход из {current_dir} в {path}")
    
    try:
        if path == "..":
            new_path = os.path.dirname(current_dir)
        elif os.path.isabs(path):
            new_path = path
        else:
            new_path = os.path.join(current_dir, path)
        
        os.chdir(new_path)
        current_dir = os.getcwd()
        print(f"Перешли в: {current_dir}")
        log.info(f"Успешный переход в {current_dir}")
    except FileNotFoundError:
        print(f"Директория не найдена: {path}")
        log.error(f"Директория не найдена: {path}")
    except PermissionError:
        print(f"Нет доступа: {path}")
        log.error(f"Нет доступа к {path}")
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка перехода: {e}")

def show_tree(depth=2):
    global current_dir
    log.info(f"Вывод дерева директорий {current_dir} глубиной {depth}")
    
    def print_tree(dir_path, prefix="", curr_depth=0):
        if curr_depth > depth:
            return
        
        try:
            items = sorted(os.listdir(dir_path))
            for i, item in enumerate(items):
                item_path = os.path.join(dir_path, item)
                is_last = (i == len(items) - 1)
                
                if os.path.isdir(item_path):
                    print(f"{prefix}{'└── ' if is_last else '├── '}{item}/")
                    extension = "    " if is_last else "│   "
                    print_tree(item_path, prefix + extension, curr_depth + 1)
        except PermissionError:
            print(f"{prefix}[Нет доступа]")
        except Exception as e:
            print(f"{prefix}[Ошибка: {e}]")
    
    print(f"\n{current_dir}")
    print_tree(current_dir)

def create_file(name):
    global current_dir
    filepath = os.path.join(current_dir, name)
    
    try:
        if os.path.exists(filepath):
            print(f"Файл уже существует: {name}")
            return False
        
        with open(filepath, 'w') as f:
            pass
        
        print(f"Файл создан: {name}")
        log.info(f"Создан файл {filepath}")
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка создания файла {filepath}: {e}")
        return False

def create_folder(path):
    global current_dir
    
    if os.path.isabs(path):
        folder_path = path
    else:
        folder_path = os.path.join(current_dir, path)
    
    try:
        os.makedirs(folder_path, exist_ok=False)
        print(f"Папка создана: {folder_path}")
        log.info(f"Создана папка {folder_path}")
        return True
    except FileExistsError:
        print(f"Папка уже существует: {path}")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка создания папки {folder_path}: {e}")
        return False

def copy_item(src, dst):
    global current_dir
    
    if os.path.isabs(src):
        src_path = src
    else:
        src_path = os.path.join(current_dir, src)
    
    if os.path.isabs(dst):
        dst_path = dst
    else:
        dst_path = os.path.join(current_dir, dst)
    
    try:
        if not os.path.exists(src_path):
            print(f"Источник не найден: {src}")
            return False
        
        if os.path.exists(dst_path):
            if not confirm(f"Цель уже существует. Перезаписать?"):
                print("Операция отменена")
                return False
        
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
        
        print(f"Скопировано: {src} -> {dst}")
        log.info(f"Скопировано {src_path} в {dst_path}")
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка копирования {src_path} в {dst_path}: {e}")
        return False

def move_item(src, dst):
    global current_dir
    
    if os.path.isabs(src):
        src_path = src
    else:
        src_path = os.path.join(current_dir, src)
    
    if os.path.isabs(dst):
        dst_path = dst
    else:
        dst_path = os.path.join(current_dir, dst)
    
    try:
        shutil.move(src_path, dst_path)
        print(f"Перемещено: {src} -> {dst}")
        log.info(f"Перемещено {src_path} в {dst_path}")
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка перемещения {src_path} в {dst_path}: {e}")
        return False

def delete_item(path):
    global current_dir
    
    if os.path.isabs(path):
        item_path = path
    else:
        item_path = os.path.join(current_dir, path)
    
    try:
        if not os.path.exists(item_path):
            print(f"Не найдено: {path}")
            return False
        
        if os.path.isfile(item_path):
            os.remove(item_path)
            print(f"Файл удалён: {path}")
            log.info(f"Удалён файл {item_path}")
        else:
            if os.listdir(item_path):
                if not confirm(f"Папка не пуста. Удалить всё?"):
                    print("Операция отменена")
                    return False
            shutil.rmtree(item_path)
            print(f"Папка удалена: {path}")
            log.info(f"Удалена папка {item_path}")
        
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка удаления {item_path}: {e}")
        return False

def search(pattern, search_dir=None):
    global current_dir
    
    if search_dir is None:
        search_dir = current_dir
    
    print(f"Поиск '{pattern}' в {search_dir}...")
    log.info(f"Поиск {pattern} в {search_dir}")
    
    try:
        path_obj = Path(search_dir)
        found = list(path_obj.rglob(pattern))
        
        if not found:
            print("Файлы не найдены")
            return []
        
        results = []
        for f in found[:100]:
            try:
                size = os.path.getsize(f) if f.is_file() else 0
                results.append([str(f), "FILE" if f.is_file() else "DIR", format_bytes(size)])
            except:
                results.append([str(f), "?", "?"])
        
        headers = ["Путь", "Тип", "Размер"]
        print_table(headers, results)
        
        if len(found) > 100:
            print(f"\n... и ещё {len(found)-100} файлов")
        
        return found
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка поиска: {e}")
        return []

def find_large_files(directory, min_mb):
    global current_dir
    
    if directory is None:
        directory = current_dir
    
    min_bytes = min_mb * 1024 * 1024
    print(f"Поиск файлов крупнее {min_mb} MB в {directory}...")
    log.info(f"Поиск файлов > {min_mb}MB в {directory}")
    
    try:
        large_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    if size > min_bytes:
                        large_files.append((filepath, size))
                except:
                    continue
        
        large_files.sort(key=lambda x: x[1], reverse=True)
        
        if not large_files:
            print("Крупные файлы не найдены")
            return []
        
        results = []
        for filepath, size in large_files[:20]:
            results.append([filepath, format_bytes(size)])
        
        headers = ["Файл", "Размер"]
        print_table(headers, results)
        
        return large_files
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка поиска крупных файлов: {e}")
        return []

def find_recent_files(directory, days):
    global current_dir
    
    if directory is None:
        directory = current_dir
    
    cutoff = datetime.now().timestamp() - (days * 86400)
    print(f"Поиск файлов изменённых за последние {days} дней в {directory}...")
    log.info(f"Поиск файлов изменённых за {days} дней в {directory}")
    
    try:
        recent_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(filepath)
                    if mtime > cutoff:
                        recent_files.append((filepath, mtime))
                except:
                    continue
        
        recent_files.sort(key=lambda x: x[1], reverse=True)
        
        if not recent_files:
            print("Недавно изменённые файлы не найдены")
            return []
        
        results = []
        for filepath, mtime in recent_files[:20]:
            mod_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            results.append([filepath, mod_date])
        
        headers = ["Файл", "Изменён"]
        print_table(headers, results)
        
        return recent_files
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка поиска недавних файлов: {e}")
        return []

def dir_stats(directory):
    global current_dir
    
    if directory is None:
        directory = current_dir
    
    print(f"Подсчёт статистики для {directory}...")
    log.info(f"Статистика директории {directory}")
    
    try:
        total_size = 0
        file_count = 0
        dir_count = 0
        extensions = {}
        largest_files = []
        
        for root, dirs, files in os.walk(directory):
            dir_count += len(dirs)
            
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    total_size += size
                    file_count += 1
                    
                    ext = os.path.splitext(file)[1].lower() or "no extension"
                    extensions[ext] = extensions.get(ext, 0) + size
                    
                    largest_files.append((filepath, size))
                except:
                    continue
        
        largest_files.sort(key=lambda x: x[1], reverse=True)
        top_files = largest_files[:10]
        
        print("\n" + "="*60)
        print("СТАТИСТИКА ДИРЕКТОРИИ")
        print("="*60)
        print(f"Путь: {directory}")
        print(f"Общий размер: {format_bytes(total_size)}")
        print(f"Количество файлов: {file_count}")
        print(f"Количество папок: {dir_count}")
        
        print("\nТоп-10 самых больших файлов:")
        for path, size in top_files:
            print(f"  {format_bytes(size)} - {path}")
        
        print("\nРазбивка по расширениям:")
        sorted_ext = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
        for ext, size in sorted_ext[:10]:
            percent = (size / total_size * 100) if total_size > 0 else 0
            print(f"  {ext}: {format_bytes(size)} ({percent:.1f}%)")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка подсчёта статистики {directory}: {e}")

def file_hash(filepath):
    global current_dir
    
    if os.path.isabs(filepath):
        path = filepath
    else:
        path = os.path.join(current_dir, filepath)
    
    try:
        if not os.path.isfile(path):
            print(f"Не файл или не существует: {filepath}")
            return None
        
        print(f"Вычисление хэшей для {path}...")
        log.info(f"Вычисление хэшей для {path}")
        
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
                sha256.update(chunk)
        
        print(f"\nMD5:    {md5.hexdigest()}")
        print(f"SHA256: {sha256.hexdigest()}")
        
        return {'md5': md5.hexdigest(), 'sha256': sha256.hexdigest()}
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка вычисления хэша {path}: {e}")
        return None

def create_zip(source, destination):
    global current_dir
    
    if os.path.isabs(source):
        src_path = source
    else:
        src_path = os.path.join(current_dir, source)
    
    if os.path.isabs(destination):
        dst_path = destination
    else:
        dst_path = os.path.join(current_dir, destination)
    
    try:
        if not dst_path.endswith('.zip'):
            dst_path += '.zip'
        
        with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isfile(src_path):
                zipf.write(src_path, os.path.basename(src_path))
            else:
                for root, dirs, files in os.walk(src_path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.relpath(filepath, os.path.dirname(src_path))
                        zipf.write(filepath, arcname)
        
        print(f"Архив создан: {dst_path}")
        log.info(f"Создан архив {dst_path} из {src_path}")
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка создания архива {dst_path}: {e}")
        return False

def extract_zip(archive, destination):
    global current_dir
    
    if os.path.isabs(archive):
        arc_path = archive
    else:
        arc_path = os.path.join(current_dir, archive)
    
    if os.path.isabs(destination):
        dst_path = destination
    else:
        dst_path = os.path.join(current_dir, destination)
    
    try:
        os.makedirs(dst_path, exist_ok=True)
        
        with zipfile.ZipFile(arc_path, 'r') as zipf:
            zipf.extractall(dst_path)
        
        print(f"Архив распакован в: {dst_path}")
        log.info(f"Распакован архив {arc_path} в {dst_path}")
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка распаковки {arc_path}: {e}")
        return False

def list_zip(archive):
    global current_dir
    
    if os.path.isabs(archive):
        arc_path = archive
    else:
        arc_path = os.path.join(current_dir, archive)
    
    try:
        with zipfile.ZipFile(arc_path, 'r') as zipf:
            items = []
            for info in zipf.infolist():
                items.append([info.filename, "DIR" if info.is_dir() else "FILE", format_bytes(info.file_size)])
            
            headers = ["Имя", "Тип", "Размер"]
            print_table(headers, items)
            print(f"\nВсего файлов: {len([i for i in items if i[1]=='FILE'])}")
        
        log.info(f"Просмотр содержимого архива {arc_path}")
    except Exception as e:
        print(f"Ошибка: {e}")
        log.error(f"Ошибка просмотра архива {arc_path}: {e}")

def run():
    global current_dir
    
    log.info("Запуск файлового менеджера")
    
    while True:
        print("\n" + "="*50)
        print("ФАЙЛОВЫЙ МЕНЕДЖЕР")
        print("="*50)
        print(f"Текущая директория: {current_dir}")
        print("-"*50)
        print("1. Показать содержимое")
        print("2. Сменить директорию")
        print("3. Дерево директорий")
        print("4. Создать файл/папку")
        print("5. Копировать/переместить")
        print("6. Удалить")
        print("7. Поиск файлов")
        print("8. Статистика директории")
        print("9. Хэш файла")
        print("10. Работа с ZIP")
        print("0. Назад")
        print("-"*50)
        
        choice = input("Выберите действие: ").strip()
        
        if choice == '0':
            log.info("Выход из файлового менеджера")
            break
        
        elif choice == '1':
            list_dir()
        
        elif choice == '2':
            path = input("Путь (.. для подъёма): ").strip()
            if path:
                change_dir(path)
        
        elif choice == '3':
            depth = input("Глубина (2): ").strip()
            depth = int(depth) if depth.isdigit() else 2
            show_tree(depth)
        
        elif choice == '4':
            print("\n1. Файл\n2. Папку")
            type_choice = input("Выберите: ").strip()
            name = input("Имя: ").strip()
            
            if type_choice == '1':
                create_file(name)
            elif type_choice == '2':
                create_folder(name)
            else:
                print("Неверный выбор")
        
        elif choice == '5':
            src = input("Источник: ").strip()
            dst = input("Назначение: ").strip()
            print("1. Копировать\n2. Переместить")
            op = input("Выберите: ").strip()
            
            if op == '1':
                copy_item(src, dst)
            elif op == '2':
                move_item(src, dst)
            else:
                print("Неверный выбор")
        
        elif choice == '6':
            path = input("Что удалить: ").strip()
            if path:
                delete_item(path)
        
        elif choice == '7':
            print("\n1. Поиск по шаблону\n2. Крупные файлы\n3. Недавние файлы")
            search_choice = input("Выберите: ").strip()
            
            if search_choice == '1':
                pattern = input("Шаблон (*.txt, test.?): ").strip()
                if pattern:
                    search(pattern)
            elif search_choice == '2':
                min_mb = input("Минимальный размер (MB): ").strip()
                if min_mb.isdigit():
                    find_large_files(current_dir, int(min_mb))
            elif search_choice == '3':
                days = input("За сколько дней: ").strip()
                if days.isdigit():
                    find_recent_files(current_dir, int(days))
            else:
                print("Неверный выбор")
        
        elif choice == '8':
            dir_stats(current_dir)
        
        elif choice == '9':
            path = input("Путь к файлу: ").strip()
            if path:
                file_hash(path)
        
        elif choice == '10':
            print("\n1. Создать архив\n2. Распаковать архив\n3. Просмотреть архив")
            zip_choice = input("Выберите: ").strip()
            
            if zip_choice == '1':
                src = input("Что архивировать: ").strip()
                dst = input("Имя архива: ").strip()
                if src and dst:
                    create_zip(src, dst)
            elif zip_choice == '2':
                arc = input("Файл архива: ").strip()
                dst = input("Папка назначения: ").strip()
                if arc and dst:
                    extract_zip(arc, dst)
            elif zip_choice == '3':
                arc = input("Файл архива: ").strip()
                if arc:
                    list_zip(arc)
            else:
                print("Неверный выбор")
        
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    run()