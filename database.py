import sqlite3
from contextlib import contextmanager
import json
from datetime import datetime

class Database:
    def __init__(self, db_path='tasks.db'):
        self.db_path = db_path
        self.create_tables()
        
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
            
    def create_tables(self):
        """Создание необходимых таблиц"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица заданий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workzilla_id TEXT UNIQUE,
                    title TEXT,
                    description TEXT,
                    requirements TEXT,
                    status TEXT,
                    platform TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Таблица коммуникаций
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS communications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    message TEXT,
                    sender TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            ''')
            
            # Таблица результатов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    screenshots TEXT,
                    completion_data TEXT,
                    verified BOOLEAN,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            ''')
            
            conn.commit()
            
    def save_task(self, task_data):
        """Сохранение задания"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (
                    workzilla_id, title, description, requirements,
                    status, platform, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_data['workzilla_id'],
                task_data['title'],
                task_data['description'],
                json.dumps(task_data['requirements']),
                'new',
                task_data['platform'],
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            return cursor.lastrowid
            
    def save_communication(self, task_id, message, sender):
        """Сохранение коммуникации"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO communications (task_id, message, sender, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (task_id, message, sender, datetime.now().isoformat()))
            
    def save_result(self, task_id, result_data):
        """Сохранение результата"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO results (
                    task_id, screenshots, completion_data,
                    verified, completed_at
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                task_id,
                json.dumps(result_data['screenshots']),
                json.dumps(result_data['completion_data']),
                False,
                datetime.now().isoformat()
            ))
            
    def update_task_status(self, task_id, status):
        """Обновление статуса задания"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks
                SET status = ?, updated_at = ?
                WHERE id = ?
            ''', (status, datetime.now().isoformat(), task_id))
            
    def get_task(self, task_id):
        """Получение информации о задании"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            return cursor.fetchone() 