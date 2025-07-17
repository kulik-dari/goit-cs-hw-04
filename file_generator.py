#!/usr/bin/env python3
"""
Генератор тестових файлів для домашнього завдання з конкурентного програмування.
Створює текстові файли з різним вмістом для тестування паралельного пошуку.
"""

import os
import random
import string
from pathlib import Path
from typing import List, Dict

class FileGenerator:
    """Клас для генерації тестових текстових файлів"""
    
    def __init__(self, output_dir: str = "test_files"):
        """
        Ініціалізація генератора файлів
        
        Args:
            output_dir: Директорія для збереження файлів
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Набір ключових слів для вставки у файли
        self.keywords = [
            "python", "programming", "algorithm", "data", "structure",
            "function", "variable", "loop", "condition", "class",
            "object", "method", "string", "integer", "boolean",
            "list", "dictionary", "tuple", "set", "module",
            "package", "import", "exception", "error", "debug",
            "test", "development", "software", "computer", "technology"
        ]
        
        # Звичайні слова для заповнення тексту
        self.common_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have",
            "i", "it", "for", "not", "on", "with", "he", "as", "you",
            "do", "at", "this", "but", "his", "by", "from", "they",
            "we", "say", "her", "she", "or", "an", "will", "my",
            "one", "all", "would", "there", "their", "what", "so",
            "up", "out", "if", "about", "who", "get", "which", "go", "me"
        ]
    
    def generate_random_text(self, word_count: int) -> str:
        """
        Генерує випадковий текст заданої довжини
        
        Args:
            word_count: Кількість слів у тексті
            
        Returns:
            Згенерований текст
        """
        words = []
        for _ in range(word_count):
            if random.random() < 0.1:  # 10% шанс вставити ключове слово
                words.append(random.choice(self.keywords))
            else:
                words.append(random.choice(self.common_words))
        
        return " ".join(words)
    
    def generate_file(self, filename: str, word_count: int = 1000, 
                     target_keywords: List[str] = None) -> None:
        """
        Генерує один текстовий файл
        
        Args:
            filename: Ім'я файлу
            word_count: Кількість слів у файлі
            target_keywords: Конкретні ключові слова для включення
        """
        filepath = self.output_dir / filename
        
        # Генеруємо основний текст
        text = self.generate_random_text(word_count)
        
        # Додаємо цільові ключові слова, якщо вказані
        if target_keywords:
            for keyword in target_keywords:
                # Вставляємо кожне ключове слово кілька разів
                for _ in range(random.randint(2, 8)):
                    text += f" {keyword}"
        
        # Форматуємо текст у параграфи
        words = text.split()
        paragraphs = []
        
        i = 0
        while i < len(words):
            paragraph_length = random.randint(50, 150)
            paragraph = " ".join(words[i:i + paragraph_length])
            paragraphs.append(paragraph)
            i += paragraph_length
        
        formatted_text = "\n\n".join(paragraphs)
        
        # Зберігаємо файл
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        print(f"✅ Створено файл: {filename} ({len(words)} слів)")
    
    def generate_test_files(self, num_files: int = 20, 
                          keywords_to_distribute: List[str] = None) -> Dict[str, List[str]]:
        """
        Генерує набір тестових файлів
        
        Args:
            num_files: Кількість файлів для створення
            keywords_to_distribute: Ключові слова для розподілу по файлах
            
        Returns:
            Словник з інформацією про розподіл ключових слів
        """
        print(f"🔧 Генерація {num_files} тестових файлів...")
        
        if keywords_to_distribute is None:
            keywords_to_distribute = ["python", "algorithm", "data", "function", "programming"]
        
        keyword_distribution = {keyword: [] for keyword in keywords_to_distribute}
        
        for i in range(1, num_files + 1):
            filename = f"file_{i:03d}.txt"
            
            # Випадково обираємо розмір файлу
            word_count = random.randint(500, 2000)
            
            # Випадково обираємо ключові слова для цього файлу
            file_keywords = []
            for keyword in keywords_to_distribute:
                if random.random() < 0.6:  # 60% шанс включити ключове слово
                    file_keywords.append(keyword)
                    keyword_distribution[keyword].append(filename)
            
            self.generate_file(filename, word_count, file_keywords)
        
        print(f"✅ Створено {num_files} файлів у директорії {self.output_dir}")
        
        # Виводимо статистику розподілу
        print("\n📊 Розподіл ключових слів:")
        for keyword, files in keyword_distribution.items():
            print(f"  {keyword}: {len(files)} файлів - {files[:5]}{'...' if len(files) > 5 else ''}")
        
        return keyword_distribution
    
    def clean_test_files(self) -> None:
        """Видаляє всі тестові файли"""
        if self.output_dir.exists():
            for file in self.output_dir.glob("*.txt"):
                file.unlink()
            print(f"🧹 Очищено директорію {self.output_dir}")

def main():
    """Головна функція для демонстрації генератора"""
    generator = FileGenerator()
    
    # Очищаємо старі файли
    generator.clean_test_files()
    
    # Генеруємо нові тестові файли
    keywords = ["python", "algorithm", "data", "function", "programming", 
                "structure", "variable", "loop", "class", "method"]
    
    distribution = generator.generate_test_files(
        num_files=30, 
        keywords_to_distribute=keywords
    )
    
    print(f"\n🎯 Готово! Тестові файли створено для пошуку ключових слів:")
    print(f"   Ключові слова: {', '.join(keywords)}")
    print(f"   Файли: {generator.output_dir}/*.txt")

if __name__ == "__main__":
    main()
