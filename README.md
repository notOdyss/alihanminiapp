# Exchange Bot - Telegram Bot with Mini App

Production-ready Telegram bot for exchange services with integrated Mini App (WebApp) built with React.

## Features

### Bot Features
- User registration and tracking
- Session tracking with engagement metrics
- FAQ system with 5 categories
- Payment methods (PayPal, Crypto, Stripe)
- Transaction logging
- Admin panel via separate logging bot
- Telegram Mini App integration

### Mini App Features
- Transaction history with VIP progress tracking
- Fee calculator for different payment methods
- Balance overview (PayPal, Stripe, Withdrawals)
- Statistics dashboard with monthly metrics
- Admin contacts
- Referral system

## Tech Stack

**Backend:**
- Python 3.11+
- aiogram 3.x (Telegram Bot Framework)
- PostgreSQL (Database)
- SQLAlchemy (ORM)
- aiohttp (Web Server for API)

**Frontend:**
- React 18
- Vite
- React Router DOM
- Telegram WebApp SDK

## Quick Start

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Setup Database

**Option A - Automated (Recommended):**
```bash
./setup_database.sh
```

**Option B - Manual:**
```bash
psql postgres -c "CREATE DATABASE exchangebot;"
psql postgres -c "CREATE USER postgres WITH PASSWORD 'postgres';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE exchangebot TO postgres;"
psql exchangebot -c "GRANT ALL ON SCHEMA public TO postgres;"
```

**Option C - Docker:**
```bash
docker run --name exchangebot-db \
  -e POSTGRES_DB=exchangebot \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15
```

### 3. Install Python Dependencies

```bash
# Install Python dependencies
pip3 install -r requirements.txt
```

### 4. Configure Environment

The `.env` file is already configured. Update if needed:

```env
BOT_TOKEN=your_main_bot_token
LOG_BOT_TOKEN=your_log_bot_token
LOG_CHAT_ID=your_telegram_user_id
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/exchangebot
ADMIN_IDS=[your_telegram_user_id]
```

### 5. Run the Bot

```bash
# This will start both the bot and API server
python3 -m bot.main
```

The bot will:
- Start on Telegram (polling)
- API server will run on http://localhost:8080
- Database tables will be created automatically on first run

## Mini App Setup

### 1. Install Frontend Dependencies

```bash
cd webapp
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

The Mini App will run on http://localhost:3000

### 3. Build for Production

```bash
npm run build
```

Deploy the `dist` folder to:
- Netlify
- Vercel
- Your own server with nginx + HTTPS

### 4. Update Bot Configuration

After deploying the Mini App, update `bot/keyboards/main.py`:

```python
WEBAPP_URL = "https://your-deployed-domain.com"
```

### 5. Register with BotFather

```
/setmenubutton
@your_bot_username
https://your-deployed-domain.com
```

## Project Structure

```
alihanbot/
├── bot/
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── connection.py      # Database manager
│   │   └── repositories/      # Data access layer
│   ├── routers/               # Bot command handlers
│   ├── keyboards/             # Inline keyboards
│   ├── services/              # Business logic
│   ├── middlewares/           # Request middlewares
│   ├── webapp/
│   │   └── api.py            # REST API for Mini App
│   ├── config.py             # Configuration
│   └── main.py               # Entry point
├── webapp/                    # React Mini App
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── context/          # Context providers
│   │   ├── pages/            # Page components
│   │   └── App.jsx
│   └── package.json
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── setup_database.sh         # Database setup script
```

## API Endpoints

The API server runs on port 8080 and provides these endpoints:

- `GET /health` - Health check
- `GET /api/profile` - User profile and stats
- `GET /api/balance` - User balance information
- `GET /api/statistics` - User statistics
- `GET /api/transactions` - Transaction history
- `POST /api/transactions` - Create transaction
- `POST /api/events` - Log Mini App events
- `GET /api/referral` - Get referral code
- `POST /api/referral` - Create referral code

Authentication uses Telegram WebApp initData validation.

## Database Schema

**users**
- id, username, first_name, last_name
- language_code, is_premium, is_blocked
- referral_code, referrer_id
- created_at, updated_at, last_active_at
- webapp_sessions, webapp_last_visit

**interactions**
- id, user_id, interaction_type, action, data
- created_at

**transactions**
- id, user_id, payment_method, amount, currency
- status, external_id
- created_at, updated_at, completed_at

## Development

### Run Bot Only

```bash
python3 -m bot.main
```

### Run Mini App Only

```bash
cd webapp
npm run dev
```

### Testing API

```bash
curl http://localhost:8080/health
```

## Deployment

### Bot Deployment

**Option 1 - VPS/Server:**
```bash
# Use systemd, supervisor, or screen
screen -S exchangebot
python3 -m bot.main
# Ctrl+A, D to detach
```

**Option 2 - Docker:**
```bash
# Build and run with docker-compose
docker-compose up -d
```

### Mini App Deployment

See `webapp/README.md` for detailed deployment instructions.

## Database Backup

```bash
# Backup
pg_dump -U postgres exchangebot > backup.sql

# Restore
psql -U postgres exchangebot < backup.sql
```

## Troubleshooting

### PostgreSQL Connection Issues

1. Check if PostgreSQL is running:
   ```bash
   pg_isready
   ```

2. Verify credentials:
   ```bash
   psql -U postgres -d exchangebot
   ```

3. Check logs:
   ```bash
   tail -f /opt/homebrew/var/log/postgresql@15.log  # macOS
   sudo journalctl -u postgresql                     # Linux
   ```

### Bot Not Starting

1. Check bot token in `.env`
2. Verify database connection
3. Check Python version: `python3 --version` (need 3.11+)
4. Check logs for errors

### Mini App Not Loading

1. Check if API server is running on port 8080
2. Verify WEBAPP_URL in `bot/keyboards/main.py`
3. Check browser console for errors
4. Ensure Mini App is served over HTTPS in production

## Remote Database Hosting

Free PostgreSQL hosting options:

- **Supabase** - https://supabase.com (500MB free)
- **Railway** - https://railway.app (500h/month free)
- **Render** - https://render.com (90 days free)
- **ElephantSQL** - https://www.elephantsql.com (20MB free)

Update `.env` with remote connection URL:
```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Telegram: @thxfortheslapali or @herr_leutenant
- GitHub Issues: Create an issue in the repository
