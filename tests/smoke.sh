#!/bin/bash
# tests/smoke.sh
# Быстрые smoke-тесты для проверки HTTP-статусов

BASE_URL="http://127.0.0.1:8000"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔥 ===== SMOKE TESTS (bash + curl) ====="
echo ""

# Тест 1: Главная страница доступна
echo -n "📄 Главная страница (/news/)... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/news/")
if [ "$HTTP" = "200" ]; then
    echo -e "${GREEN}✅ $HTTP${NC}"
else
    echo -e "${RED}❌ $HTTP${NC}"
fi

# Тест 2: Страница входа
echo -n "🔐 Страница входа... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/accounts/login/")
if [ "$HTTP" = "200" ]; then
    echo -e "${GREEN}✅ $HTTP${NC}"
else
    echo -e "${RED}❌ $HTTP${NC}"
fi

# Тест 3: Страница регистрации
echo -n "📝 Страница регистрации... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/accounts/signup/")
if [ "$HTTP" = "200" ]; then
    echo -e "${GREEN}✅ $HTTP${NC}"
else
    echo -e "${RED}❌ $HTTP${NC}"
fi

# Тест 4: CRUD без авторизации (должен быть 302 на login)
echo -n "🚫 Создание без авторизации... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/news/news/create/")
if [ "$HTTP" = "302" ]; then
    echo -e "${GREEN}✅ $HTTP (редирект на login)${NC}"
else
    echo -e "${YELLOW}⚠️  $HTTP${NC}"
fi

# Тест 5: Поиск доступен
echo -n "🔍 Страница поиска... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/news/search/")
if [ "$HTTP" = "200" ]; then
    echo -e "${GREEN}✅ $HTTP${NC}"
else
    echo -e "${RED}❌ $HTTP${NC}"
fi

# Тест 6: CSS файл доступен
echo -n "🎨 CSS файл... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/static/css/navigation.css")
if [ "$HTTP" = "200" ]; then
    echo -e "${GREEN}✅ $HTTP${NC}"
else
    echo -e "${YELLOW}⚠️  $HTTP (возможно, нужен collectstatic)${NC}"
fi

# Тест 7: Админка доступна
echo -n "🛠️  Админка... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/admin/")
if [ "$HTTP" = "302" ] || [ "$HTTP" = "200" ]; then
    echo -e "${GREEN}✅ $HTTP${NC}"
else
    echo -e "${RED}❌ $HTTP${NC}"
fi

# Тест 8: Flatpages
echo -n "📄 Flatpages (/pages/)... "
HTTP=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/pages/")
if [ "$HTTP" = "200" ] || [ "$HTTP" = "404" ]; then
    echo -e "${GREEN}✅ $HTTP${NC}"
else
    echo -e "${RED}❌ $HTTP${NC}"
fi

echo ""
echo "🎉 Smoke tests завершены!"
echo ""
echo "💡 Для полных pytest тестов запусти: pytest tests/ -v"