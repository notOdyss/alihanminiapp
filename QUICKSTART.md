# Quick Start Guide

Get your Exchange Bot running in 5 minutes!

## Step 1: Install PostgreSQL

Choose your operating system:

### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Windows
Download from: https://www.postgresql.org/download/windows/

### Docker (All platforms)
```bash
docker run --name exchangebot-db \
  -e POSTGRES_DB=exchangebot \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15
```

## Step 2: Setup Database

**Easy way:**
```bash
./setup_database.sh
```

**Manual way:**
```bash
psql postgres << EOF
CREATE DATABASE exchangebot;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE exchangebot TO postgres;
\c exchangebot
GRANT ALL ON SCHEMA public TO postgres;
EOF
```

## Step 3: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

## Step 4: Run the Bot

```bash
python3 -m bot.main
```

That's it! The bot is now running and will:
- Start polling for Telegram messages
- Run API server on http://localhost:8080
- Create all database tables automatically

## Next Steps

### Setup Mini App (Optional)

1. Install frontend dependencies:
   ```bash
   cd webapp
   npm install
   ```

2. Run development server:
   ```bash
   npm run dev
   ```

3. Open http://localhost:3000

### Deploy Mini App

See `webapp/README.md` for deployment instructions.

## Verify Everything Works

### Check Bot
Send `/start` to your bot on Telegram

### Check API
```bash
curl http://localhost:8080/health
```

Should return:
```json
{"status":"healthy","timestamp":"..."}
```

### Check Database
```bash
psql -U postgres -d exchangebot -c "\dt"
```

Should show tables:
- users
- interactions
- transactions
- education_sessions

## Using Remote PostgreSQL

Want to use a cloud database? Update `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

Free options:
- **Supabase** - https://supabase.com
- **Railway** - https://railway.app
- **Render** - https://render.com

## Troubleshooting

**PostgreSQL not running?**
```bash
# macOS
brew services start postgresql@15

# Linux
sudo systemctl start postgresql

# Check if running
pg_isready
```

**Can't connect to database?**
```bash
# Test connection
psql -U postgres -d exchangebot

# If it fails, recreate database
./setup_database.sh
```

**Bot not starting?**
1. Check `.env` file has correct BOT_TOKEN
2. Check database is running: `pg_isready`
3. Check Python version: `python3 --version` (need 3.11+)

**Port 8080 already in use?**
Another service is using port 8080. Either:
1. Stop the other service
2. Change port in `bot/main.py` (line 58)

## What's Next?

1. Read full documentation: `README.md`
2. Deploy Mini App: `webapp/README.md`
3. Learn about database: `DATABASE_SETUP.md`
4. Customize bot features in `bot/routers/`

## Support

Need help?
- Check `DATABASE_SETUP.md` for database issues
- Check `README.md` for full documentation
- Contact admins: @thxfortheslapali or @herr_leutenant
