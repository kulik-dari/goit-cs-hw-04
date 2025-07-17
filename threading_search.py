#!/usr/bin/env python3
"""
Багатопотокова версія програми пошуку ключових слів у текстових файлах.
Використовує модуль threading для паралельної обробки файлів.
"""

import os
import time
import threading
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
import re

class ThreadingFileSearcher:
    """Клас для багатопотокового пошуку ключових слів у файлах"""
    
    def __init__(self, num_threads: int = 4):
        """
        Ініціалізація пошукача
        
        Args:
            num_threads: Кількість потоків для обробки
        """
        self.num_threads = num_threads
        self.results = defaultdict(list)
        self.results_lock = threading.Lock()
        self.error_count = 0
        self.processed_files = 0
        self.total_files = 0
        
    def search_keywords_in_file(self, filepath: str, keywords: List[str]) -> Dict[str, bool]:
        """
        Шукає ключові слова в одному файлі
        
        Args:
            filepath: Шлях до файлу
            keywords: Список ключових слів для пошуку
            
        Returns:
            Словник з результатами пошуку для кожного ключового слова
        """
        found_keywords = {}
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read().lower()
                
                for keyword in keywords:
                    # Використовуємо регулярні вирази для точного пошуку слів
                    pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                    found_keywords[keyword] = bool(re.search(pattern, content))
                    
        except Exception as e:
            print(f"❌ Помилка при обробці файлу {filepath}: {e}")
            with self.results_lock:
                self.error_count += 1
            # Повертаємо порожній результат у випадку помилки
            found_keywords = {keyword: False for keyword in keywords}
        
        return found_keywords
    
    def worker_thread(self, file_chunk: List[str], keywords: List[str], thread_id: int):
        """
        Робочий потік для обробки частини файлів
        
        Args:
            file_chunk: Список файлів для обробки цим потоком
            keywords: Ключові слова для пошуку
            thread_id: Ідентифікатор потоку
        """
        local_results = defaultdict(list)
        files_processed = 0
        
        for filepath in file_chunk:
            try:
                found_keywords = self.search_keywords_in_file(filepath, keywords)
                
                # Додаємо файл до результатів для кожного знайденого ключового слова
                for keyword, found in found_keywords.items():
                    if found:
                        local_results[keyword].append(filepath)
                
                files_processed += 1
                
                # Періодично виводимо прогрес
                if files_processed % 5 == 0:
                    print(f"🔍 Потік {thread_id}: оброблено {files_processed}/{len(file_chunk)} файлів")
                    
            except Exception as e:
                print(f"❌ Критична помилка в потоці {thread_id} при обробці {filepath}: {e}")
                with self.results_lock:
                    self.error_count += 1
        
        # Безпечно об'єднуємо результати з глобальними
        with self.results_lock:
            for keyword, file_list in local_results.items():
                self.results[keyword].extend(file_list)
            self.processed_files += files_processed
        
        print(f"✅ Потік {thread_id}: завершено обробку {files_processed} файлів")
    
    def split_files_into_chunks(self, file_list: List[str]) -> List[List[str]]:
        """
        Розділяє список файлів на частини для потоків
        
        Args:
            file_list: Список всіх файлів
            
        Returns:
            Список частин файлів для кожного потоку
        """
        chunk_size = len(file_list) // self.num_threads
        remainder = len(file_list) % self.num_threads
        
        chunks = []
        start = 0
        
        for i in range(self.num_threads):
            # Розподіляємо залишок між першими потоками
            end = start + chunk_size + (1 if i < remainder else 0)
            
            if start < len(file_list):
                chunks.append(file_list[start:end])
            else:
                chunks.append([])  # Порожній чанк, якщо файлів менше ніж потоків
            
            start = end
        
        return chunks
    
    def search_files(self, directory: str, keywords: List[str], 
                    file_pattern: str = "*.txt") -> Dict[str, List[str]]:
        """
        Головна функція для багатопотокового пошуку
        
        Args:
            directory: Директорія з файлами
            keywords: Список ключових слів для пошуку
            file_pattern: Шаблон для пошуку файлів
            
        Returns:
            Словник з результатами: {ключове_слово: [список_файлів]}
        """
        print(f"🚀 Запуск багатопотокового пошуку...")
        print(f"📁 Директорія: {directory}")
        print(f"🔍 Ключові слова: {', '.join(keywords)}")
        print(f"🧵 Кількість потоків: {self.num_threads}")
        
        # Знаходимо всі файли для обробки
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Директорія {directory} не існує")
        
        file_list = list(directory_path.glob(file_pattern))
        file_paths = [str(f) for f in file_list]
        
        if not file_paths:
            print(f"⚠️  Файли за шаблоном {file_pattern} не знайдені у {directory}")
            return {}
        
        self.total_files = len(file_paths)
        print(f"📄 Знайдено файлів: {self.total_files}")
        
        # Скидаємо результати
        self.results.clear()
        self.error_count = 0
        self.processed_files = 0
        
        # Засікаємо час
        start_time = time.time()
        
        # Розділяємо файли між потоками
        file_chunks = self.split_files_into_chunks(file_paths)
        
        print(f"📊 Розподіл файлів по потоках:")
        for i, chunk in enumerate(file_chunks):
            print(f"   Потік {i+1}: {len(chunk)} файлів")
        
        # Створюємо і запускаємо потоки
        threads = []
        for i, chunk in enumerate(file_chunks):
            if chunk:  # Створюємо потік тільки якщо є файли для обробки
                thread = threading.Thread(
                    target=self.worker_thread,
                    args=(chunk, keywords, i + 1)
                )
                threads.append(thread)
                thread.start()
        
        # Очікуємо завершення всіх потоків
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Виводимо статистику
        print(f"\n📈 Статистика виконання:")
        print(f"   ⏱️  Час виконання: {execution_time:.2f} секунд")
        print(f"   📁 Оброблено файлів: {self.processed_files}/{self.total_files}")
        print(f"   ❌ Помилок: {self.error_count}")
        print(f"   🚀 Швидкість: {self.processed_files/execution_time:.1f} файлів/сек")
        
        # Конвертуємо результати у звичайний словник
        final_results = dict(self.results)
        
        print(f"\n🎯 Результати пошуку:")
        for keyword in keywords:
            files_found = len(final_results.get(keyword, []))
            print(f"   '{keyword}': знайдено у {files_found} файлах")
        
        return final_results

def main():
    """Демонстрація роботи багатопотокового пошукача"""
    
    # Налаштування
    search_directory = "test_files"
    keywords_to_search = ["python", "algorithm", "data", "function", "programming"]
    num_threads = 4
    
    # Перевіряємо наявність тестових файлів
    if not Path(search_directory).exists():
        print(f"❌ Директорія {search_directory} не існує!")
        print("💡 Спочатку запустіть file_generator.py для створення тестових файлів")
        return
    
    try:
        # Створюємо пошукач
        searcher = ThreadingFileSearcher(num_threads=num_threads)
        
        # Виконуємо пошук
        results = searcher.search_files(
            directory=search_directory,
            keywords=keywords_to_search
        )
        
        # Детальний вивід результатів
        print(f"\n" + "="*60)
        print("📋 ДЕТАЛЬНІ РЕЗУЛЬТАТИ ПОШУКУ")
        print("="*60)
        
        for keyword, files in results.items():
            print(f"\n🔍 Ключове слово: '{keyword}'")
            if files:
                print(f"   Знайдено у {len(files)} файлах:")
                for file_path in sorted(files):
                    filename = Path(file_path).name
                    print(f"     • {filename}")
            else:
                print("   ❌ Не знайдено в жодному файлі")
        
        # Підсумок
        total_matches = sum(len(files) for files in results.values())
        print(f"\n📊 Загальний підсумок:")
        print(f"   🎯 Всього співпадінь: {total_matches}")
        print(f"   📝 Ключових слів: {len(keywords_to_search)}")
        print(f"   🧵 Потоків використано: {num_threads}")
        
    except Exception as e:
        print(f"❌ Критична помилка: {e}")

if __name__ == "__main__":
    main()
