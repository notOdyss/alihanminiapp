#!/bin/bash

# PostgreSQL Database Setup Script for Exchange Bot

echo "🗄️  Exchange Bot - PostgreSQL Setup"
echo "===================================="
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed!"
    echo ""
    echo "Install PostgreSQL:"
    echo "  macOS:   brew install postgresql@15"
    echo "  Ubuntu:  sudo apt install postgresql postgresql-contrib"
    echo "  Windows: https://www.postgresql.org/download/windows/"
    exit 1
fi

echo "✅ PostgreSQL is installed"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "⚠️  PostgreSQL is not running. Starting it..."

    # Try to start PostgreSQL based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew services start postgresql@15 2>/dev/null || brew services start postgresql 2>/dev/null
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo systemctl start postgresql
    fi

    sleep 2

    if ! pg_isready -q; then
        echo "❌ Failed to start PostgreSQL. Please start it manually."
        exit 1
    fi
fi

echo "✅ PostgreSQL is running"
echo ""

# Database configuration
DB_NAME="exchangebot"
DB_USER="postgres"
DB_PASSWORD="postgres"

echo "Creating database and user..."
echo ""

# Create database
psql postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Database '$DB_NAME' created"
else
    echo "⚠️  Database '$DB_NAME' already exists (skipping)"
fi

# Create user (might already exist)
psql postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ User '$DB_USER' created"
else
    echo "⚠️  User '$DB_USER' already exists (skipping)"
fi

# Grant privileges
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null
psql $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null
echo "✅ Privileges granted"
echo ""

# Verify connection
echo "Verifying database connection..."
if psql -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database connection successful!"
else
    echo "❌ Failed to connect to database"
    exit 1
fi

echo ""
echo "===================================="
echo "✅ Database setup complete!"
echo ""
echo "Connection details:"
echo "  Database: $DB_NAME"
echo "  User:     $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Host:     localhost"
echo "  Port:     5432"
echo ""
echo "Connection URL (already in .env):"
echo "  postgresql+asyncpg://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "Next steps:"
echo "  1. Run the bot: python3 -m bot.main"
echo "  2. Tables will be created automatically on first run"
echo ""
