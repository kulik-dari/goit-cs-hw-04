#!/usr/bin/env python3
"""
Багатопроцесорна версія програми пошуку ключових слів у текстових файлах.
Використовує модуль multiprocessing для паралельної обробки файлів.
"""

import os
import time
import multiprocessing
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import re

def search_keywords_in_file(filepath: str, keywords: List[str]) -> Tuple[str, Dict[str, bool]]:
    """
    Шукає ключові слова в одному файлі (функція для multiprocessing)
    
    Args:
        filepath: Шлях до файлу
        keywords: Список ключових слів для пошуку
        
    Returns:
        Кортеж: (шлях_до_файлу, {ключове_слово: знайдено})
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
        # Повертаємо порожній результат у випадку помилки
        found_keywords = {keyword: False for keyword in keywords}
    
    return filepath, found_keywords

def worker_process(file_chunk: List[str], keywords: List[str], 
                  process_id: int, result_queue: multiprocessing.Queue):
    """
    Робочий процес для обробки частини файлів
    
    Args:
        file_chunk: Список файлів для обробки цим процесом
        keywords: Ключові слова для пошуку
        process_id: Ідентифікатор процесу
        result_queue: Черга для передачі результатів
    """
    try:
        local_results = defaultdict(list)
        files_processed = 0
        error_count = 0
        
        print(f"🚀 Процес {process_id}: почав обробку {len(file_chunk)} файлів")
        
        for filepath in file_chunk:
            try:
                file_path, found_keywords = search_keywords_in_file(filepath, keywords)
                
                # Додаємо файл до результатів для кожного знайденого ключового слова
                for keyword, found in found_keywords.items():
                    if found:
                        local_results[keyword].append(file_path)
                
                files_processed += 1
                
                # Періодично виводимо прогрес
                if files_processed % 5 == 0:
                    print(f"🔍 Процес {process_id}: оброблено {files_processed}/{len(file_chunk)} файлів")
                    
            except Exception as e:
                print(f"❌ Помилка в процесі {process_id} при обробці {filepath}: {e}")
                error_count += 1
        
        # Відправляємо результати через чергу
        result_data = {
            'process_id': process_id,
            'results': dict(local_results),
            'files_processed': files_processed,
            'errors': error_count
        }
        
        result_queue.put(result_data)
        print(f"✅ Процес {process_id}: завершено обробку {files_processed} файлів, помилок: {error_count}")
        
    except Exception as e:
        print(f"❌ Критична помилка в процесі {process_id}: {e}")
        # Відправляємо інформацію про помилку
        result_queue.put({
            'process_id': process_id,
            'results': {},
            'files_processed': 0,
            'errors': 1,
            'critical_error': str(e)
        })

class MultiprocessingFileSearcher:
    """Клас для багатопроцесорного пошуку ключових слів у файлах"""
    
    def __init__(self, num_processes: int = None):
        """
        Ініціалізація пошукача
        
        Args:
            num_processes: Кількість процесів (за замовчуванням - кількість CPU)
        """
        if num_processes is None:
            self.num_processes = multiprocessing.cpu_count()
        else:
            self.num_processes = max(1, num_processes)
        
        self.total_files = 0
        self.processed_files = 0
        self.error_count = 0
    
    def split_files_into_chunks(self, file_list: List[str]) -> List[List[str]]:
        """
        Розділяє список файлів на частини для процесів
        
        Args:
            file_list: Список всіх файлів
            
        Returns:
            Список частин файлів для кожного процесу
        """
        chunk_size = len(file_list) // self.num_processes
        remainder = len(file_list) % self.num_processes
        
        chunks = []
        start = 0
        
        for i in range(self.num_processes):
            # Розподіляємо залишок між першими процесами
            end = start + chunk_size + (1 if i < remainder else 0)
            
            if start < len(file_list):
                chunks.append(file_list[start:end])
            else:
                chunks.append([])  # Порожній чанк, якщо файлів менше ніж процесів
            
            start = end
        
        return chunks
    
    def search_files(self, directory: str, keywords: List[str], 
                    file_pattern: str = "*.txt") -> Dict[str, List[str]]:
        """
        Головна функція для багатопроцесорного пошуку
        
        Args:
            directory: Директорія з файлами
            keywords: Список ключових слів для пошуку
            file_pattern: Шаблон для пошуку файлів
            
        Returns:
            Словник з результатами: {ключове_слово: [список_файлів]}
        """
        print(f"🚀 Запуск багатопроцесорного пошуку...")
        print(f"📁 Директорія: {directory}")
        print(f"🔍 Ключові слова: {', '.join(keywords)}")
        print(f"⚙️  Кількість процесів: {self.num_processes}")
        
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
        
        # Скидаємо лічильники
        self.processed_files = 0
        self.error_count = 0
        
        # Засікаємо час
        start_time = time.time()
        
        # Розділяємо файли між процесами
        file_chunks = self.split_files_into_chunks(file_paths)
        
        print(f"📊 Розподіл файлів по процесах:")
        for i, chunk in enumerate(file_chunks):
            print(f"   Процес {i+1}: {len(chunk)} файлів")
        
        # Створюємо чергу для результатів
        result_queue = multiprocessing.Queue()
        
        # Створюємо і запускаємо процеси
        processes = []
        for i, chunk in enumerate(file_chunks):
            if chunk:  # Створюємо процес тільки якщо є файли для обробки
                process = multiprocessing.Process(
                    target=worker_process,
                    args=(chunk, keywords, i + 1, result_queue)
                )
                processes.append(process)
                process.start()
        
        # Збираємо результати з черги
        final_results = defaultdict(list)
        processes_completed = 0
        
        while processes_completed < len(processes):
            try:
                # Очікуємо результат з таймаутом
                result_data = result_queue.get(timeout=30)
                
                process_id = result_data['process_id']
                process_results = result_data['results']
                files_processed = result_data['files_processed']
                errors = result_data['errors']
                
                # Об'єднуємо результати
                for keyword, file_list in process_results.items():
                    final_results[keyword].extend(file_list)
                
                self.processed_files += files_processed
                self.error_count += errors
                
                processes_completed += 1
                
                if 'critical_error' in result_data:
                    print(f"⚠️  Процес {process_id} завершився з критичною помилкою: {result_data['critical_error']}")
                
            except Exception as e:
                print(f"❌ Помилка при отриманні результатів: {e}")
                break
        
        # Очікуємо завершення всіх процесів
        for process in processes:
            process.join(timeout=10)
            if process.is_alive():
                print(f"⚠️  Примусове завершення процесу {process.pid}")
                process.terminate()
                process.join()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Виводимо статистику
        print(f"\n📈 Статистика виконання:")
        print(f"   ⏱️  Час виконання: {execution_time:.2f} секунд")
        print(f"   📁 Оброблено файлів: {self.processed_files}/{self.total_files}")
        print(f"   ❌ Помилок: {self.error_count}")
        if execution_time > 0:
            print(f"   🚀 Швидкість: {self.processed_files/execution_time:.1f} файлів/сек")
        
        # Конвертуємо результати у звичайний словник
        results = dict(final_results)
        
        print(f"\n🎯 Результати пошуку:")
        for keyword in keywords:
            files_found = len(results.get(keyword, []))
            print(f"   '{keyword}': знайдено у {files_found} файлах")
        
        return results

def main():
    """Демонстрація роботи багатопроцесорного пошукача"""
    
    # Налаштування
    search_directory = "test_files"
    keywords_to_search = ["python", "algorithm", "data", "function", "programming"]
    num_processes = multiprocessing.cpu_count()
    
    # Перевіряємо наявність тестових файлів
    if not Path(search_directory).exists():
        print(f"❌ Директорія {search_directory} не існує!")
        print("💡 Спочатку запустіть file_generator.py для створення тестових файлів")
        return
    
    try:
        # Створюємо пошукач
        searcher = MultiprocessingFileSearcher(num_processes=num_processes)
        
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
        print(f"   ⚙️  Процесів використано: {num_processes}")
        
    except Exception as e:
        print(f"❌ Критична помилка: {e}")

if __name__ == "__main__":
    main()
