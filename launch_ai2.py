#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Получаем текущую директорию скрипта
SCRIPT_DIR = Path(__file__).resolve().parent

# Добавляем директорию проекта в sys.path
sys.path.append(str(SCRIPT_DIR))

from ai_system import AI2
from database import Database
import logging
from datetime import datetime
import time

def setup_logging():
    log_dir = SCRIPT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        filename=log_dir / f"ai2_launcher_{datetime.now().strftime('%Y%m%d')}.log",
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

def main():
    try:
        setup_logging()
        logging.info("Starting AI2...")
        
        print("Initializing AI2 (Task Executor)...")
        db = Database(db_path=str(SCRIPT_DIR / "tasks.db"))
        ai2 = AI2(config_path=str(SCRIPT_DIR / "config.json"))
        
        print("AI2 is running. Waiting for tasks...")
        print("Press Ctrl+C to stop")
        
        # Основной цикл работы
        while True:
            try:
                # Получение заданий для выполнения
                tasks = db.get_tasks_for_execution()
                for task in tasks:
                    logging.info(f"Executing task {task['id']}")
                    print(f"Processing task: {task['title']}")
                    
                    # Выполнение задания
                    result = ai2.execute_task(task)
                    
                    # Сохранение результата
                    if result['status'] == 'success':
                        db.save_result(task['id'], result)
                        db.update_task_status(task['id'], 'completed')
                        print(f"Task {task['id']} completed successfully")
                    else:
                        logging.error(f"Task {task['id']} failed: {result['error']}")
                        
                # Пауза между проверками
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\nStopping AI2...")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
                continue
                
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 