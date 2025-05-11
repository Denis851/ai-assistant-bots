from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai
from datetime import datetime
import json
import os
import logging
from PIL import Image
import pyautogui
import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class AI1(object):
    """Аналитик и Коммуникатор"""
    
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        self.setup_logging()
        self.setup_nlp()
        self.setup_browser()
        self.setup_gpt()
        
    def load_config(self, config_path):
        """Загрузка конфигурации"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        self.keywords = set(self.config['keywords'])
        self.stop_words = set(self.config['stop_words'])
        
    def setup_logging(self):
        """Настройка логирования"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logging.basicConfig(
            filename=f"logs/ai1_{datetime.now().strftime('%Y%m%d')}.log",
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        
    def setup_nlp(self):
        """Настройка NLP компонентов"""
        nltk.download('punkt')
        nltk.download('stopwords')
        self.nlp_stop_words = set(stopwords.words('russian'))
        
    def setup_browser(self):
        """Настройка браузера"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Фоновый режим
        self.browser = webdriver.Chrome(options=options)
        
    def setup_gpt(self):
        """Настройка GPT"""
        openai.api_key = self.config['openai_api_key']
        
    def analyze_task(self, task_text):
        """Анализ текста задания"""
        tokens = word_tokenize(task_text.lower())
        
        # Проверка на стоп-слова
        if any(word in tokens for word in self.stop_words):
            return False, "Содержит стоп-слова"
            
        # Проверка на ключевые слова
        found_keywords = set(tokens) & self.keywords
        if not found_keywords:
            return False, "Нет ключевых слов"
            
        return True, list(found_keywords)
        
    def communicate_with_client(self, task_id, message):
        """Общение с клиентом через GPT"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.config['gpt_system_prompt']},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"GPT Error for task {task_id}: {str(e)}")
            return None
            
    def verify_task(self, task_id, result):
        """Проверка выполненного задания"""
        # Проверка скриншотов
        screenshots = result.get('screenshots', [])
        if not screenshots:
            return False, "Нет скриншотов выполнения"
            
        # Проверка соответствия ТЗ
        requirements = self.get_task_requirements(task_id)
        if not self.check_requirements(result, requirements):
            return False, "Не соответствует ТЗ"
            
        return True, "Задание выполнено корректно"
        
    def mark_task_complete(self, task_id):
        """Отметка о выполнении задания на платформе"""
        try:
            self.browser.get(f"{self.config['workzilla_url']}/task/{task_id}")
            complete_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "complete-button"))
            )
            complete_button.click()
            return True
        except Exception as e:
            logging.error(f"Error marking task {task_id} complete: {str(e)}")
            return False

class AI2(object):
    """Исполнитель"""
    
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        self.setup_logging()
        self.setup_browser()
        
    def load_config(self, config_path):
        """Загрузка конфигурации"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
    def setup_logging(self):
        """Настройка логирования"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logging.basicConfig(
            filename=f"logs/ai2_{datetime.now().strftime('%Y%m%d')}.log",
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        
    def setup_browser(self):
        """Настройка браузера"""
        options = webdriver.ChromeOptions()
        self.browser = webdriver.Chrome(options=options)  # Видимый режим для выполнения
        
    def execute_task(self, task):
        """Выполнение задания"""
        try:
            # Переход на нужную платформу
            self.browser.get(task['platform_url'])
            
            # Выполнение действий согласно ТЗ
            for action in task['actions']:
                self.execute_action(action)
                
            # Создание скриншотов
            screenshots = self.take_screenshots()
            
            return {
                'status': 'success',
                'screenshots': screenshots,
                'completion_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error executing task {task['id']}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def execute_action(self, action):
        """Выполнение конкретного действия"""
        if action['type'] == 'click':
            element = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, action['selector']))
            )
            element.click()
        elif action['type'] == 'input':
            element = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, action['selector']))
            )
            element.send_keys(action['value'])
        time.sleep(action.get('delay', 1))
        
    def take_screenshots(self):
        """Создание скриншотов"""
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"{screenshots_dir}/screenshot_{timestamp}.png"
        
        # Создание скриншота всей страницы
        self.browser.save_screenshot(screenshot_path)
        
        # Создание скриншота активной области
        active_screenshot = pyautogui.screenshot()
        active_screenshot.save(f"{screenshots_dir}/active_{timestamp}.png")
        
        return [screenshot_path, f"{screenshots_dir}/active_{timestamp}.png"] 