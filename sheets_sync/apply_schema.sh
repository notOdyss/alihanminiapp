#!/bin/bash
# Применение SQL схемы к базе данных

# Загрузка переменных окружения
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

echo "======================================================================"
echo "ПРИМЕНЕНИЕ SQL СХЕМЫ ДЛЯ GOOGLE SHEETS SYNC"
echo "======================================================================"
echo ""

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL не установлен в .env"
    exit 1
fi

# Извлечение параметров из DATABASE_URL
# Формат: postgresql+asyncpg://username:password@host:port/database
# Для psql нужен формат: postgresql://username:password@host:port/database

PSQL_URL=$(echo $DATABASE_URL | sed 's/postgresql+asyncpg/postgresql/')

echo "📊 База данных: $PSQL_URL"
echo ""
echo "Применение схемы database_schema.sql..."
echo ""

psql "$PSQL_URL" -f database_schema.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✅ СХЕМА УСПЕШНО ПРИМЕНЕНА!"
    echo "======================================================================"
    echo ""
    echo "Можно запускать sync сервис:"
    echo "  python3 sheets_sync/sync_service.py"
    echo ""
else
    echo ""
    echo "======================================================================"
    echo "❌ ОШИБКА ПРИ ПРИМЕНЕНИИ СХЕМЫ"
    echo "======================================================================"
    echo ""
    exit 1
fi
