#!/usr/bin/env python3
"""
fix_links.py
Скрипт для замены Markdown-ссылок на HTML с target="_blank"

Использование:
    python tools/fix_links.py

Файл для обработки:
    docs/auth_specification.md
"""

import re
import os
from pathlib import Path

# Пути (относительно корня проекта)
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
MD_FILE = ROOT_DIR / 'docs' / 'auth_specification.md'


def fix_links():
    """Заменяет [📸](../img/filename.png) на <a href="../img/filename.png" target="_blank">📸</a>"""

    if not MD_FILE.exists():
        print(f"❌ Файл не найден: {MD_FILE}")
        return False

    # Читаем файл
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Считаем количество ссылок до замены
    old_count = len(re.findall(r'\[📸\]\(\.\./img/', content))

    # Заменяем
    pattern = r'\[📸\]\(\.\./img/([^)]+)\)'
    replacement = r'<a href="../img/\1" target="_blank">📸</a>'
    content = re.sub(pattern, replacement, content)

    # Считаем количество ссылок после замены
    new_count = len(re.findall(r'target="_blank"', content))

    # Записываем обратно
    with open(MD_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Файл {MD_FILE} обновлён!")
    print(f"📸 Заменено ссылок: {old_count} → {new_count}")
    print(f"🔗 Все скриншоты теперь открываются в новой вкладке")

    return True


if __name__ == '__main__':
    fix_links()