# 📋 News Portal — Список задач

## 🔴 Критические (блокируют релиз)
- [ ] #EMAIL-001: Протестировать рассылку на реальном SMTP (не console)
- [ ] #SUB-001: Реализовать UI кнопки «Подписаться/Отписаться» на категории

## 🟡 Технические долги
- [ ] #DELETE-001: Реализовать PostDelete view и заменить заглушки в urls.py
  - Файл: `news/urls.py` (строки ~35-36)
  - Файл: `news/views.py` (добавить класс PostDelete)
  - Шаблоны: `post_delete.html` уже готов
  - Приоритет: после email-уведомлений

## 🟢 Улучшения (не блокируют)
- [ ] Исправить предупреждение `UnorderedObjectListWarning` в PostList
- [ ] Обновить deprecated настройки allauth (`ACCOUNT_EMAIL_REQUIRED` → `ACCOUNT_SIGNUP_FIELDS`)

---
*Последнее обновление: 2026-03-03*
*Для поиска: grep -r "TODO(#" --include="*.py" --include="*.md"*