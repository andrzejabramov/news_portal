#!/usr/bin/env python3
"""
Вывод структуры проекта в виде дерева.
Использование: python tools/show_structure.py [--max-depth N] [--show-size]
"""

import os
import sys
from pathlib import Path

# Папки/файлы, которые игнорируем (как в .gitignore)
IGNORE_PATTERNS = {
    '__pycache__', '.git', '.venv', 'venv', 'env', '.env',
    '.pytest_cache', 'htmlcov', '.coverage', '*.pyc', '*.pyo',
    '.DS_Store', 'db.sqlite3', 'db.backup.sqlite', '*.log',
    'staticfiles', 'media', 'uploads', 'parcing', 'img',
    '.mypy_cache', '.ruff_cache', 'node_modules', '.next'
}


def should_ignore(path: Path) -> bool:
    """Проверяем, нужно ли игнорировать путь"""
    name = path.name
    # Игнорируем по имени
    if name in IGNORE_PATTERNS or name.startswith('.'):
        return True
    # Игнорируем по расширению
    if path.suffix in {'.pyc', '.pyo', '.log', '.sqlite3'}:
        return True
    return False


def print_tree(
        path: Path,
        prefix: str = '',
        depth: int = 0,
        max_depth: int = None,
        show_size: bool = False
):
    """Рекурсивно печатает дерево"""
    if max_depth is not None and depth > max_depth:
        return

    try:
        entries = sorted(
            [e for e in path.iterdir() if not should_ignore(e)],
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
    except PermissionError:
        return

    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        connector = '└── ' if is_last else '├── '

        # Размер файла (опционально)
        size_str = ''
        if show_size and entry.is_file():
            size_bytes = entry.stat().st_size
            if size_bytes < 1024:
                size_str = f' ({size_bytes} B)'
            elif size_bytes < 1024 * 1024:
                size_str = f' ({size_bytes / 1024:.1f} KB)'
            else:
                size_str = f' ({size_bytes / 1024 / 1024:.1f} MB)'

        print(f"{prefix}{connector}{entry.name}{size_str}")

        if entry.is_dir():
            extension = '    ' if is_last else '│   '
            print_tree(
                entry,
                prefix + extension,
                depth + 1,
                max_depth,
                show_size
            )


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Показать структуру проекта')
    parser.add_argument('--max-depth', type=int, help='Максимальная глубина')
    parser.add_argument('--show-size', action='store_true', help='Показать размер файлов')
    parser.add_argument('--output', type=str, help='Сохранить в файл')
    args = parser.parse_args()

    root = Path(__file__).parent.parent.resolve()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            original_stdout = sys.stdout
            sys.stdout = f
            print(f"📁 Структура проекта: {root}")
            print("=" * 60)
            print_tree(root, max_depth=args.max_depth, show_size=args.show_size)
            sys.stdout = original_stdout
        print(f"✅ Структура сохранена в {args.output}")
    else:
        print(f"📁 Структура проекта: {root}")
        print("=" * 60)
        print_tree(root, max_depth=args.max_depth, show_size=args.show_size)


if __name__ == '__main__':
    main()