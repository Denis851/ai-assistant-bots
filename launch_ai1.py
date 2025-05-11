#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Получаем текущую директорию скрипта
SCRIPT_DIR = Path(__file__).resolve().parent

# Добавляем директорию проекта в sys.path
sys.path.append(str(SCRIPT_DIR))

from ai_system import AI1
from database import Database
import logging
from datetime import datetime

def setup_logging():
    log_dir = SCRIPT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        filename=log_dir / f"ai1_launcher_{datetime.now().strftime('%Y%m%d')}.log",
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

def main():
    try:
        setup_logging()
        logging.info("Starting AI1...")
        
        print("Initializing AI1 (Analyst & Communicator)...")
        db = Database(db_path=str(SCRIPT_DIR / "tasks.db"))
        ai1 = AI1(config_path=str(SCRIPT_DIR / "config.json"))
        
        print("AI1 is running. Monitoring for new tasks...")
        print("Press Ctrl+C to stop")
        
        # Основной цикл работы
        while True:
            try:
                # Проверка новых заданий
                tasks = ai1.get_new_tasks()
                for task in tasks:
                    # Анализ задания
                    is_valid, keywords = ai1.analyze_task(task['description'])
                    if is_valid:
                        logging.info(f"Processing task {task['workzilla_id']}")
                        print(f"New task found: {task['title']}")
                        
                        # Сохранение задания
                        task_id = db.save_task(task)
                        
                        # Коммуникация с клиентом
                        response = ai1.communicate_with_client(
                            task_id,
                            f"Новое задание: {task['title']}"
                        )
                        if response:
                            db.save_communication(task_id, response, 'AI1')
                            
            except KeyboardInterrupt:
                print("\nStopping AI1...")
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