#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import sys

def create_info_plist(app_name):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.ai.{app_name}</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSBackgroundOnly</key>
    <false/>
</dict>
</plist>'''

def check_required_files():
    required_files = ['ai_system.py', 'database.py', 'config.json']
    current_dir = Path.cwd()
    missing_files = []
    
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("Ошибка: Не найдены следующие файлы:")
        for file in missing_files:
            print(f"- {file}")
        sys.exit(1)

def create_launcher_script(script_path, ai_num):
    with open(script_path, 'w') as f:
        f.write(f'''#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Получаем директорию скрипта
SCRIPT_DIR = Path(__file__).resolve().parent

# Добавляем директорию проекта в sys.path
sys.path.append(str(SCRIPT_DIR))

from ai_system import AI{ai_num}
from database import Database
import logging
from datetime import datetime
import time

def setup_logging():
    log_dir = SCRIPT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        filename=log_dir / f"ai{ai_num}_launcher_{{datetime.now().strftime('%Y%m%d')}}.log",
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

def main():
    try:
        setup_logging()
        logging.info(f"Starting AI{ai_num}...")
        
        print(f"Initializing AI{ai_num}...")
        db = Database(db_path=str(SCRIPT_DIR / "tasks.db"))
        ai = AI{ai_num}(config_path=str(SCRIPT_DIR / "config.json"))
        
        print(f"AI{ai_num} is running...")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                time.sleep(1)  # Добавляем задержку чтобы не нагружать процессор
            except KeyboardInterrupt:
                print(f"\\nStopping AI{ai_num}...")
                break
            except Exception as e:
                logging.error(f"Error: {{str(e)}}")
                continue
                
    except Exception as e:
        logging.error(f"Critical error: {{str(e)}}")
        print(f"Error: {{str(e)}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
''')

def main():
    try:
        # Проверяем наличие необходимых файлов
        check_required_files()
        
        # Получаем абсолютный путь к текущей директории
        current_dir = Path.cwd()
        
        # Создаем директорию для приложений
        apps_dir = current_dir / "apps"
        apps_dir.mkdir(exist_ok=True)
        
        # Создаем launcher скрипты
        for ai_num in [1, 2]:
            launcher_script = current_dir / f"launch_ai{ai_num}.py"
            create_launcher_script(launcher_script, ai_num)
            os.chmod(launcher_script, 0o755)
            print(f"Created launch_ai{ai_num}.py")
        
        # Копируем необходимые файлы в директорию приложений
        for file in ['ai_system.py', 'database.py', 'config.json']:
            shutil.copy2(current_dir / file, apps_dir / file)
        
        # Создаем приложения
        for ai_num in [1, 2]:
            app_name = f"Launch_AI{ai_num}"
            script_name = f"launch_ai{ai_num}.py"
            
            # Создаем структуру директорий приложения
            app_dir = apps_dir / f"{app_name}.app"
            contents_dir = app_dir / "Contents"
            macos_dir = contents_dir / "MacOS"
            resources_dir = contents_dir / "Resources"
            
            # Создаем все необходимые директории
            for dir_path in [macos_dir, resources_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Создаем Info.plist
            with open(contents_dir / "Info.plist", 'w') as f:
                f.write(create_info_plist(app_name))
            
            # Создаем исполняемый скрипт
            runner_script = macos_dir / app_name
            with open(runner_script, 'w') as f:
                f.write('#!/bin/bash\n\n')
                f.write(f'cd "{apps_dir}"\n')
                f.write('export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"\n')
                f.write('export PYTHONPATH="${PYTHONPATH}:$(pwd)"\n\n')
                f.write(f'if ! command -v python3 &> /dev/null; then\n')
                f.write('    osascript -e \'display alert "Python не установлен" message "Пожалуйста, установите Python 3"\'\n')
                f.write('    exit 1\n')
                f.write('fi\n\n')
                f.write(f'python3 "{current_dir}/{script_name}"\n')
            
            # Делаем скрипт исполняемым
            os.chmod(runner_script, 0o755)
            
            print(f"Created {app_name}.app")
        
        print("\nУспешно создано!")
        print(f"Приложения созданы в: {apps_dir}")
        print("\nДля запуска:")
        print("1. Откройте папку apps/")
        print("2. Запустите нужное приложение двойным щелчком")
        print("\nЕсли приложения не запускаются:")
        print("1. Откройте Системные настройки -> Безопасность и конфиденциальность")
        print("2. Разрешите запуск приложений из неизвестных источников")
        print("3. При первом запуске нажмите правой кнопкой мыши -> Открыть")
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 