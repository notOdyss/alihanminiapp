# Exchange Bot Mini App

Modern Telegram Mini App for exchange bot with beautiful UI and full feature parity.

## Features

- Transaction history with VIP progress tracking
- Fee calculator for different payment methods
- Balance overview (PayPal, Stripe, Withdrawals)
- Statistics dashboard with monthly metrics
- Admin contacts and referral system
- Fully responsive design
- Telegram theming support

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Configure API URL in `.env`:
```
VITE_API_URL=http://localhost:8080
```

4. Start development server:
```bash
npm run dev
```

5. Build for production:
```bash
npm run build
```

## Deployment

### Deploy to Vercel (Recommended)

#### Method 1: Using Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. For production:
```bash
vercel --prod
```

#### Method 2: Using Vercel Dashboard

1. Push code to GitHub repository

2. Go to https://vercel.com/new

3. Import your GitHub repository: `https://github.com/notOdyss/alihanminiapp`

4. Configure project:
   - Framework Preset: **Vite**
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

5. Add Environment Variables (optional):
   - `VITE_API_URL` = `https://your-api-domain.com`

6. Click **Deploy**

7. Your Mini App will be live at: `https://your-project.vercel.app`

#### Method 3: Deploy Button

Click the button below to deploy:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/notOdyss/alihanminiapp)

#### After Deployment

1. Copy your Vercel URL (e.g., `https://alihanminiapp.vercel.app`)

2. Update API URL environment variable in Vercel dashboard:
   - Go to Project Settings → Environment Variables
   - Add `VITE_API_URL` = `https://your-backend-api.com`
   - Redeploy

3. Update bot configuration in `.env`:
```bash
WEBAPP_URL=https://alihanminiapp.vercel.app/
```

4. Register with BotFather:
```
/setmenubutton
@your_bot_username
https://alihanminiapp.vercel.app
```

### Using Netlify

1. Push to GitHub
2. Go to https://app.netlify.com/start
3. Import repository
4. Build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
5. Deploy

### Using nginx

1. Build the project
2. Copy `dist` folder to nginx web root
3. Configure nginx to serve the Mini App with HTTPS

Example nginx config:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    root /path/to/webapp/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Update Bot Configuration

After deployment, update the Mini App URL in `.env`:

```bash
WEBAPP_URL=https://your-domain.com
```

## API Endpoints

The Mini App connects to these backend endpoints:

- `GET /api/balance` - Get user balance
- `GET /api/statistics` - Get user statistics
- `GET /api/transactions` - Get transaction history
- `GET /api/referral` - Get referral code
- `POST /api/referral` - Create referral code

## Tech Stack

- React 18
- Vite
- React Router DOM
- Telegram WebApp SDK
- Modern CSS with animations
