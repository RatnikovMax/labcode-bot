import os
import argparse
from pathlib import Path


class CodeCollector:
    def __init__(self):
        self.default_extensions = {
            'python': ['.py'],
            'web': ['.html', '.css', '.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'cpp': ['.cpp', '.c', '.h', '.hpp'],
            'config': ['.json', '.xml', '.yaml', '.yml'],
            'docs': ['.md', '.txt', '.rst']
        }

        self.ignore_dirs = [
            '__pycache__', '.git', 'venv', 'env', 'node_modules',
            '.idea', 'build', 'dist', '.vscode', '__pycache__',
            'target', '.gradle', '.settings', '.venv'
        ]

        self.ignore_files = [
            'package-lock.json', 'yarn.lock', '.DS_Store'
        ]

    def collect_code(self, project_path, output_file, file_types=None, max_file_size=1024 * 1024):
        """
        Собирает код проекта в один файл

        Args:
            project_path (str): Путь к проекту
            output_file (str): Выходной файл
            file_types (list): Типы файлов для включения
            max_file_size (int): Максимальный размер файла для обработки (в байтах)
        """
        if file_types is None:
            file_types = ['python']  # По умолчанию только Python

        # Собираем все расширения из выбранных типов
        extensions = []
        for file_type in file_types:
            if file_type in self.default_extensions:
                extensions.extend(self.default_extensions[file_type])

        project_path = Path(project_path)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Записываем заголовок
            outfile.write(f"СБОРКА КОДА ПРОЕКТА: {project_path.name}\n")
            outfile.write(f"ВРЕМЯ: {self._get_timestamp()}\n")
            outfile.write("=" * 100 + "\n\n")

            file_count = 0
            total_size = 0

            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    # Проверяем, нужно ли игнорировать файл
                    if self._should_ignore(file_path):
                        continue

                    # Проверяем расширение
                    if file_path.suffix.lower() not in extensions:
                        continue

                    # Проверяем размер файла
                    try:
                        file_size = file_path.stat().st_size
                        if file_size > max_file_size:
                            print(f"Пропущен (слишком большой): {file_path}")
                            continue
                    except OSError:
                        continue

                    try:
                        # Читаем содержимое файла
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()

                        # Записываем в выходной файл
                        relative_path = file_path.relative_to(project_path)
                        outfile.write(f"\n{'=' * 80}\n")
                        outfile.write(f"ФАЙЛ: {relative_path}\n")
                        outfile.write(f"РАЗМЕР: {file_size} байт\n")
                        outfile.write(f"{'=' * 80}\n\n")
                        outfile.write(content)
                        outfile.write('\n\n')

                        file_count += 1
                        total_size += len(content.encode('utf-8'))

                        print(f"✓ Обработан: {relative_path}")

                    except UnicodeDecodeError:
                        print(f"✗ Ошибка кодировки: {file_path}")
                    except Exception as e:
                        print(f"✗ Ошибка: {file_path} - {e}")

            # Записываем статистику
            outfile.write(f"\n{'=' * 100}\n")
            outfile.write(f"СТАТИСТИКА:\n")
            outfile.write(f"- Обработано файлов: {file_count}\n")
            outfile.write(f"- Общий размер кода: {total_size} байт\n")
            outfile.write(f"- Дата сборки: {self._get_timestamp()}\n")

    def _should_ignore(self, file_path):
        """Проверяет, нужно ли игнорировать файл/папку"""
        # Проверяем папки
        for part in file_path.parts:
            if part in self.ignore_dirs:
                return True

        # Проверяем файлы
        if file_path.name in self.ignore_files:
            return True

        return False

    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def show_available_types(self):
        """Показывает доступные типы файлов"""
        print("Доступные типы файлов:")
        for file_type, extensions in self.default_extensions.items():
            print(f"  {file_type}: {', '.join(extensions)}")


def main():
    parser = argparse.ArgumentParser(description='Сборка всего кода проекта в один файл')
    parser.add_argument('project_path', nargs='?', default='.',
                        help='Путь к проекту (по умолчанию: текущая директория)')
    parser.add_argument('-o', '--output', default='all_project_code.txt',
                        help='Имя выходного файла')
    parser.add_argument('-t', '--types', nargs='+',
                        choices=['python', 'web', 'java', 'cpp', 'config', 'docs'],
                        default=['python'],
                        help='Типы файлов для включения')
    parser.add_argument('--list-types', action='store_true',
                        help='Показать доступные типы файлов')

    args = parser.parse_args()

    collector = CodeCollector()

    if args.list_types:
        collector.show_available_types()
        return

    print(f"Начинаем сборку кода...")
    print(f"Проект: {args.project_path}")
    print(f"Выходной файл: {args.output}")
    print(f"Типы файлов: {', '.join(args.types)}")
    print("-" * 50)

    collector.collect_code(args.project_path, args.output, args.types)

    print("-" * 50)
    print(f"Сборка завершена! Результат сохранен в {args.output}")


if __name__ == "__main__":
    main()