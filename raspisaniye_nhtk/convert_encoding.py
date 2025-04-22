import os
import sys

def convert_to_utf8(filepath):
    """Конвертирует файл в UTF-8"""
    try:
        # Пробуем определить исходную кодировку
        encodings = ['cp1251', 'utf-8', 'utf-8-sig', 'iso-8859-1']
        
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    content = f.read()
                
                # Если чтение успешно, перезаписываем в UTF-8
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Успешно конвертирован: {filepath}")
                return
            except UnicodeDecodeError:
                continue
        
        print(f"Не удалось определить кодировку: {filepath}")
    except Exception as e:
        print(f"Ошибка при конвертации {filepath}: {str(e)}")

def main():
    print("Конвертация JSON-файлов в UTF-8...")
    
    # Обрабатываем все JSON-файлы в проекте
    for root, _, files in os.walk('.'):
        for file in files:
            if file.lower().endswith('.json'):
                full_path = os.path.join(root, file)
                convert_to_utf8(full_path)
    
    print("Конвертация завершена")

if __name__ == "__main__":
    main()