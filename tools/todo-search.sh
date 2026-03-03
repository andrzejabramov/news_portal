#!/bin/bash
# Поиск всех TODO-комментариев в проекте

echo "🔍 Поиск TODO-комментариев..."
echo "================================"

grep -rn "TODO(#" --include="*.py" --include="*.md" . | grep -v "__pycache__" | grep -v ".git"

echo "================================"
echo "✅ Поиск завершён"
