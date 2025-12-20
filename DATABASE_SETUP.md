# PostgreSQL Database Setup

The bot now uses PostgreSQL instead of SQLite for better concurrent access support and production reliability.

## Installation

### macOS (using Homebrew)

```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Or start manually
pg_ctl -D /opt/homebrew/var/postgresql@15 start
```

### Ubuntu/Debian

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Windows

Download and install from: https://www.postgresql.org/download/windows/

## Database Setup

### Option 1: Quick Setup (Recommended)

```bash
# Create database and user
psql postgres -c "CREATE DATABASE exchangebot;"
psql postgres -c "CREATE USER postgres WITH PASSWORD 'postgres';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE exchangebot TO postgres;"

# For PostgreSQL 15+, grant schema privileges
psql exchangebot -c "GRANT ALL ON SCHEMA public TO postgres;"
```

### Option 2: Using psql Interactive Shell

```bash
# Connect to PostgreSQL
psql postgres

# In psql shell:
CREATE DATABASE exchangebot;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE exchangebot TO postgres;

# Connect to the new database
\c exchangebot

# Grant schema privileges (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO postgres;

# Exit
\q
```

### Option 3: Custom Credentials

If you want to use different credentials, update `.env`:

```env
DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost:5432/your_database
```

Then create the database with your credentials:

```bash
psql postgres -c "CREATE DATABASE your_database;"
psql postgres -c "CREATE USER your_user WITH PASSWORD 'your_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE your_database TO your_user;"
psql your_database -c "GRANT ALL ON SCHEMA public TO your_user;"
```

## Using Docker (Alternative)

If you prefer Docker:

```bash
# Run PostgreSQL in Docker
docker run --name exchangebot-db \
  -e POSTGRES_DB=exchangebot \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15

# Database will be available at localhost:5432
```

## Verification

Check if PostgreSQL is running:

```bash
# Check if service is running
pg_isready

# Connect to database
psql -U postgres -d exchangebot

# List tables (after running the bot once)
\dt

# Exit
\q
```

## First Run

After setting up PostgreSQL:

```bash
# The bot will automatically create all tables on first run
python3 -m bot.main
```

## Connection Issues

If you get connection errors:

1. **"Connection refused"** - PostgreSQL service is not running
   ```bash
   brew services start postgresql@15  # macOS
   sudo systemctl start postgresql    # Linux
   ```

2. **"Authentication failed"** - Wrong credentials
   - Check your `.env` DATABASE_URL
   - Verify user exists: `psql postgres -c "\du"`

3. **"Database does not exist"** - Database not created
   - Create it: `psql postgres -c "CREATE DATABASE exchangebot;"`

4. **"Permission denied"** - Missing privileges
   ```bash
   psql exchangebot -c "GRANT ALL ON SCHEMA public TO postgres;"
   ```

## Remote PostgreSQL

To use a remote PostgreSQL server (e.g., Railway, Render, Supabase):

1. Get your connection URL from the provider
2. Update `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   ```

Popular free PostgreSQL hosting:
- **Supabase** - https://supabase.com (500MB free)
- **Railway** - https://railway.app (500h/month free)
- **Render** - https://render.com (90 days free)
- **ElephantSQL** - https://www.elephantsql.com (20MB free)

## Migration from SQLite

If you have existing data in `bot.db`:

1. Export data from SQLite
2. Import into PostgreSQL
3. Update `.env` to use PostgreSQL URL

Or simply start fresh - the bot will create empty tables automatically.

## Backup

Backup your PostgreSQL database:

```bash
# Backup
pg_dump -U postgres exchangebot > backup.sql

# Restore
psql -U postgres exchangebot < backup.sql
```

## Advantages Over SQLite

- ✅ Concurrent connections (bot + API server)
- ✅ Better performance at scale
- ✅ Advanced features (JSON columns, full-text search, etc.)
- ✅ Production-ready
- ✅ Can be hosted remotely
- ✅ Better data integrity and ACID compliance
