#!/usr/bin/env python3
"""
Скрипт для порівняння продуктивності багатопотокового та багатопроцесорного підходів
до пошуку ключових слів у текстових файлах.
"""

import time
import multiprocessing
from pathlib import Path
from typing import Dict, List
import statistics

# Імпортуємо наші класи пошукачів
from threading_search import ThreadingFileSearcher
from multiprocessing_search import MultiprocessingFileSearcher

class PerformanceBenchmark:
    """Клас для проведення бенчмарків продуктивності"""
    
    def __init__(self, test_directory: str = "test_files"):
        """
        Ініціалізація бенчмарка
        
        Args:
            test_directory: Директорія з тестовими файлами
        """
        self.test_directory = test_directory
        self.keywords = ["python", "algorithm", "data", "function", "programming"]
        self.results = {}
    
    def run_threading_benchmark(self, num_threads_list: List[int], 
                               num_runs: int = 3) -> Dict[int, Dict[str, float]]:
        """
        Бенчмарк багатопотокового підходу з різною кількістю потоків
        
        Args:
            num_threads_list: Список кількості потоків для тестування
            num_runs: Кількість запусків для усереднення
            
        Returns:
            Словник з результатами: {кількість_потоків: {метрика: значення}}
        """
        print(f"🧵 Тестування багатопотокового підходу...")
        threading_results = {}
        
        for num_threads in num_threads_list:
            print(f"\n📊 Тестування з {num_threads} потоками...")
            run_times = []
            
            for run in range(num_runs):
                print(f"   Запуск {run + 1}/{num_runs}")
                
                searcher = ThreadingFileSearcher(num_threads=num_threads)
                
                start_time = time.time()
                results = searcher.search_files(
                    directory=self.test_directory,
                    keywords=self.keywords
                )
                end_time = time.time()
                
                execution_time = end_time - start_time
                run_times.append(execution_time)
                
                print(f"      Час виконання: {execution_time:.2f}с")
            
            # Обчислюємо статистики
            avg_time = statistics.mean(run_times)
            min_time = min(run_times)
            max_time = max(run_times)
            std_dev = statistics.stdev(run_times) if len(run_times) > 1 else 0
            
            threading_results[num_threads] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'std_dev': std_dev,
                'runs': run_times
            }
            
            print(f"   📈 Середній час: {avg_time:.2f}с (±{std_dev:.2f})")
        
        return threading_results
    
    def run_multiprocessing_benchmark(self, num_processes_list: List[int], 
                                    num_runs: int = 3) -> Dict[int, Dict[str, float]]:
        """
        Бенчмарк багатопроцесорного підходу з різною кількістю процесів
        
        Args:
            num_processes_list: Список кількості процесів для тестування
            num_runs: Кількість запусків для усереднення
            
        Returns:
            Словник з результатами: {кількість_процесів: {метрика: значення}}
        """
        print(f"⚙️  Тестування багатопроцесорного підходу...")
        multiprocessing_results = {}
        
        for num_processes in num_processes_list:
            print(f"\n📊 Тестування з {num_processes} процесами...")
            run_times = []
            
            for run in range(num_runs):
                print(f"   Запуск {run + 1}/{num_runs}")
                
                searcher = MultiprocessingFileSearcher(num_processes=num_processes)
                
                start_time = time.time()
                results = searcher.search_files(
                    directory=self.test_directory,
                    keywords=self.keywords
                )
                end_time = time.time()
                
                execution_time = end_time - start_time
                run_times.append(execution_time)
                
                print(f"      Час виконання: {execution_time:.2f}с")
            
            # Обчислюємо статистики
            avg_time = statistics.mean(run_times)
            min_time = min(run_times)
            max_time = max(run_times)
            std_dev = statistics.stdev(run_times) if len(run_times) > 1 else 0
            
            multiprocessing_results[num_processes] = {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'std_dev': std_dev,
                'runs': run_times
            }
            
            print(f"   📈 Середній час: {avg_time:.2f}с (±{std_dev:.2f})")
        
        return multiprocessing_results
    
    def run_sequential_benchmark(self, num_runs: int = 3) -> Dict[str, float]:
        """
        Бенчмарк послідовного (одного потоку) підходу для порівняння
        
        Args:
            num_runs: Кількість запусків для усереднення
            
        Returns:
            Словник з результатами
        """
        print(f"📝 Тестування послідовного підходу (1 потік)...")
        run_times = []
        
        for run in range(num_runs):
            print(f"   Запуск {run + 1}/{num_runs}")
            
            searcher = ThreadingFileSearcher(num_threads=1)
            
            start_time = time.time()
            results = searcher.search_files(
                directory=self.test_directory,
                keywords=self.keywords
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            run_times.append(execution_time)
            
            print(f"      Час виконання: {execution_time:.2f}с")
        
        # Обчислюємо статистики
        avg_time = statistics.mean(run_times)
        min_time = min(run_times)
        max_time = max(run_times)
        std_dev = statistics.stdev(run_times) if len(run_times) > 1 else 0
        
        sequential_results = {
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'std_dev': std_dev,
            'runs': run_times
        }
        
        print(f"   📈 Середній час: {avg_time:.2f}с (±{std_dev:.2f})")
        return sequential_results
    
    def analyze_results(self, threading_results: Dict, multiprocessing_results: Dict, 
                       sequential_results: Dict) -> None:
        """
        Аналізує та виводить результати бенчмарків
        
        Args:
            threading_results: Результати багатопотокового підходу
            multiprocessing_results: Результати багатопроцесорного підходу
            sequential_results: Результати послідовного підходу
        """
        print(f"\n" + "="*80)
        print("📊 АНАЛІЗ РЕЗУЛЬТАТІВ ПРОДУКТИВНОСТІ")
        print("="*80)
        
        sequential_time = sequential_results['avg_time']
        
        print(f"\n📝 Послідовний підхід (базовий):")
        print(f"   Час: {sequential_time:.2f}с (±{sequential_results['std_dev']:.2f})")
        
        print(f"\n🧵 Багатопотоковий підхід:")
        print(f"{'Потоки':<8} {'Час (с)':<10} {'Прискорення':<12} {'Ефективність':<12}")
        print("-" * 45)
        
        best_threading_time = float('inf')
        best_threading_threads = 1
        
        for threads, results in sorted(threading_results.items()):
            avg_time = results['avg_time']
            speedup = sequential_time / avg_time
            efficiency = speedup / threads * 100
            
            print(f"{threads:<8} {avg_time:<10.2f} {speedup:<12.2f} {efficiency:<12.1f}%")
            
            if avg_time < best_threading_time:
                best_threading_time = avg_time
                best_threading_threads = threads
        
        print(f"\n⚙️  Багатопроцесорний підхід:")
        print(f"{'Процеси':<8} {'Час (с)':<10} {'Прискорення':<12} {'Ефективність':<12}")
        print("-" * 45)
        
        best_multiprocessing_time = float('inf')
        best_multiprocessing_processes = 1
        
        for processes, results in sorted(multiprocessing_results.items()):
            avg_time = results['avg_time']
            speedup = sequential_time / avg_time
            efficiency = speedup / processes * 100
            
            print(f"{processes:<8} {avg_time:<10.2f} {speedup:<12.2f} {efficiency:<12.1f}%")
            
            if avg_time < best_multiprocessing_time:
                best_multiprocessing_time = avg_time
                best_multiprocessing_processes = processes
        
        print(f"\n🏆 ПІДСУМОК:")
        print(f"   📝 Послідовний підхід: {sequential_time:.2f}с")
        print(f"   🧵 Кращий threading: {best_threading_time:.2f}с ({best_threading_threads} потоків)")
        print(f"   ⚙️  Кращий multiprocessing: {best_multiprocessing_time:.2f}с ({best_multiprocessing_processes} процесів)")
        
        # Визначаємо переможця
        if best_threading_time < best_multiprocessing_time:
            winner = "Threading"
            winner_time = best_threading_time
            loser_time = best_multiprocessing_time
        else:
            winner = "Multiprocessing"
            winner_time = best_multiprocessing_time
            loser_time = best_threading_time
        
        improvement = ((loser_time - winner_time) / loser_time) * 100
        
        print(f"\n🎯 Переможець: {winner}")
        print(f"   Швидше на {improvement:.1f}% від конкурента")
        print(f"   Прискорення відносно послідовного: {sequential_time/winner_time:.2f}x")

def main():
    """Головна функція для запуску бенчмарків"""
    
    # Перевіряємо наявність тестових файлів
    test_directory = "test_files"
    if not Path(test_directory).exists():
        print(f"❌ Директорія {test_directory} не існує!")
        print("💡 Спочатку запустіть file_generator.py для створення тестових файлів")
        return
    
    # Параметри тестування
    cpu_count = multiprocessing.cpu_count()
    threads_to_test = [1, 2, 4, cpu_count] if cpu_count > 4 else [1, 2, cpu_count]
    processes_to_test = [1, 2, 4, cpu_count] if cpu_count > 4 else [1, 2, cpu_count]
    num_runs = 3
    
    print(f"🚀 Запуск бенчмарків продуктивності")
    print(f"📁 Тестова директорія: {test_directory}")
    print(f"💻 Доступно CPU: {cpu_count}")
    print(f"🔄 Кількість запусків на тест: {num_runs}")
    print(f"🧵 Потоки для тестування: {threads_to_test}")
    print(f"⚙️  Процеси для тестування: {processes_to_test}")
    
    try:
        benchmark = PerformanceBenchmark(test_directory)
        
        # Запускаємо тести
        print(f"\n🏁 Початок тестування...")
        
        # Послідовний підхід (базовий)
        sequential_results = benchmark.run_sequential_benchmark(num_runs)
        
        # Багатопотоковий підхід
        threading_results = benchmark.run_threading_benchmark(threads_to_test, num_runs)
        
        # Багатопроцесорний підхід
        multiprocessing_results = benchmark.run_multiprocessing_benchmark(processes_to_test, num_runs)
        
        # Аналіз результатів
        benchmark.analyze_results(threading_results, multiprocessing_results, sequential_results)
        
        print(f"\n✅ Бенчмарк завершено!")
        
    except Exception as e:
        print(f"❌ Помилка під час бенчмарку: {e}")

if __name__ == "__main__":
    main()
