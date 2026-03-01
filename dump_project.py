#!/usr/bin/env python3
"""
Скрипт для дампа всего проекта в один текстовый файл.
Включает: исходный код, SQL-схемы, конфиги, документацию.
Исключает: логи, кэш, бинарники, git.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# =============================================================================
# КОНФИГУРАЦИЯ
# =============================================================================

# Корень проекта (где лежит этот скрипт)
ROOT = Path(__file__).parent

# Папка для вывода дампов
OUTPUT_DIR = ROOT / "parcing"
OUTPUT_FILE = OUTPUT_DIR / f"project_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# =============================================================================
# ЦЕЛЕВЫЕ ДИРЕКТОРИИ (включая все сервисы)
# =============================================================================
TARGET_DIRS = [
    # Сервисы
    "auth",
    "users",
    "webhook_2can",

    # Базы данных и SQL
    "sql",
    "payment_reply",

    # Скрипты и утилиты
    "ai_scripts",

    # Документация
    "docs",
]

# =============================================================================
# РАЗРЕШЁННЫЕ РАСШИРЕНИЯ ФАЙЛОВ
# =============================================================================
ALLOWED_EXTENSIONS = {
    # Python
    ".py",
    # SQL
    ".sql", ".sql.template",
    # Конфиги
    ".yaml", ".yml", ".json", ".toml", ".ini", ".conf", ".env", ".env.example",
    # Docker
    "Dockerfile", ".dockerignore",
    # Shell
    ".sh", ".bash",
    # Документация
    ".md", ".txt", ".rst",
    # Web (если есть)
    ".html", ".css", ".js", ".ts",
    # Templates
    ".j2", ".jinja2", ".html",
    # Прочее
    ".gitignore", ".editorconfig", "requirements.txt", "Makefile", "README",
}

# =============================================================================
# ИСКЛЮЧЕНИЯ (ПАПКИ И ФАЙЛЫ)
# =============================================================================
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "eggs",
    "*.egg-info",
}

IGNORE_FILES = {
    # Бинарники и кэш
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.dylib",
    # Базы данных и дампы
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "*.dump",
    "*.bak",
    # Логи
    "*.log",
    "*.logs",
    "*.logs.zip",
    # Временные файлы
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
    # Скомпилированные
    "*.class",
    "*.o",
    "*.a",
}


# =============================================================================
# ФУНКЦИИ
# =============================================================================

def is_ignored_dir(path: Path) -> bool:
    """Проверка, является ли папка игнорируемой."""
    for part in path.parts:
        if part in IGNORE_DIRS or part.startswith("."):
            return True
    return False


def is_ignored_file(path: Path) -> bool:
    """Проверка, является ли файл игнорируемым."""
    # Проверка по имени
    if path.name in IGNORE_FILES:
        return True

    # Проверка по расширению
    if path.suffix and path.suffix not in ALLOWED_EXTENSIONS:
        # Исключение для файлов без расширения (Dockerfile, Makefile, etc.)
        if path.name not in ["Dockerfile", "Makefile", "README", ".gitignore", ".dockerignore"]:
            return True

    # Проверка на вхождение паттернов в путь
    path_str = str(path)
    for pattern in IGNORE_FILES:
        if pattern.startswith("*") and pattern[1:] in path_str:
            return True

    # Исключаем файлы в папке parcing (чтобы не дампить сами дампы)
    if "parcing" in path.parts:
        return True

    return False


def get_file_size_mb(path: Path) -> float:
    """Получить размер файла в МБ."""
    try:
        return path.stat().st_size / (1024 * 1024)
    except:
        return 0.0


def dump_file(file_path: Path, out_handle, root_path: Path):
    """Записать содержимое файла в дамп."""
    rel_path = file_path.relative_to(root_path)

    # Проверка размера (пропускаем файлы > 5 МБ)
    file_size = get_file_size_mb(file_path)
    if file_size > 5.0:
        out_handle.write(f"\n### SKIPPED (>{file_size:.1f}MB): {rel_path} ###\n\n")
        return

    out_handle.write(f"\n{'=' * 80}\n")
    out_handle.write(f"### FILE: {rel_path} ###\n")
    out_handle.write(f"### SIZE: {file_size:.2f} MB ###\n")
    out_handle.write(f"{'=' * 80}\n\n")

    try:
        # Пробуем разные кодировки
        content = None
        for encoding in ["utf-8", "latin-1", "cp1251"]:
            try:
                content = file_path.read_text(encoding=encoding, errors="ignore")
                break
            except:
                continue

        if content:
            out_handle.write(content)
            if not content.endswith("\n"):
                out_handle.write("\n")
        else:
            out_handle.write("[ERROR: Could not decode file]\n")

    except Exception as e:
        out_handle.write(f"[ERROR READING FILE: {type(e).__name__}: {e}]\n")

    out_handle.write(f"\n{'=' * 80}\n")
    out_handle.write(f"### END OF FILE: {rel_path} ###\n")
    out_handle.write(f"{'=' * 80}\n\n")


def write_tree_structure(out_handle, root_path: Path):
    """Записать структуру дерева файлов в начало дампа."""
    out_handle.write("=" * 80 + "\n")
    out_handle.write("PROJECT STRUCTURE\n")
    out_handle.write("=" * 80 + "\n\n")

    try:
        import subprocess
        result = subprocess.run(
            ["tree", "-L", "4", "-I",
             "|".join(["__pycache__", "*.pyc", ".git", "node_modules", "venv", ".venv", "*.log", "*.logs.zip"])],
            cwd=root_path,
            capture_output=True,
            text=True,
            errors="ignore"
        )
        out_handle.write(result.stdout)
    except FileNotFoundError:
        out_handle.write("[tree command not found, skipping structure]\n")
    except Exception as e:
        out_handle.write(f"[Error generating tree: {e}]\n")

    out_handle.write("\n\n")


def main():
    """Основная функция."""
    print("=" * 60)
    print("PROJECT DUMP SCRIPT")
    print("=" * 60)
    print(f"Root: {ROOT}")
    print(f"Output: {OUTPUT_FILE}")
    print("=" * 60)

    # Создаем папку для вывода
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Счётчики
    files_count = 0
    dirs_count = 0
    total_size = 0

    print("\nScanning project...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        # Заголовок
        out.write("#" * 80 + "\n")
        out.write(f"# PROJECT DUMP\n")
        out.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"# Root: {ROOT}\n")
        out.write(f"# Output: {OUTPUT_FILE}\n")
        out.write("#" * 80 + "\n\n")

        # Структура проекта
        print("Generating project structure...")
        write_tree_structure(out, ROOT)

        # Проходим по целевым папкам
        for target in TARGET_DIRS:
            target_path = ROOT / target
            if not target_path.exists():
                print(f"⚠️  Warning: Directory '{target}' not found, skipping.")
                continue

            print(f"📁 Processing: {target}/")
            dirs_count += 1

            for file_path in sorted(target_path.rglob("*")):
                if file_path.is_file():
                    if is_ignored_dir(file_path):
                        continue
                    if is_ignored_file(file_path):
                        continue

                    dump_file(file_path, out, ROOT)
                    files_count += 1
                    total_size += file_path.stat().st_size

        # Важные файлы из корня
        print("📁 Processing root files...")
        root_files = [
            "docker-compose.yml",
            "docker-compose.yml.example",
            ".env.example",
            ".gitignore",
            "README.md",
            "requirements.txt",
            "Makefile",
        ]

        for fname in root_files:
            f_path = ROOT / fname
            if f_path.exists() and not is_ignored_file(f_path):
                dump_file(f_path, out, ROOT)
                files_count += 1
                total_size += f_path.stat().st_size

    # Итоговый отчёт
    print("\n" + "=" * 60)
    print("DUMP COMPLETE!")
    print("=" * 60)
    print(f"📁 Directories processed: {dirs_count}")
    print(f"📄 Files processed: {files_count}")
    print(f"💾 Total size: {total_size / (1024 * 1024):.2f} MB")
    print(f"📦 Output file: {OUTPUT_FILE}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())