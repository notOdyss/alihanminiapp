# Deploy to Vercel - Step by Step Guide

This guide will help you deploy the Mini App to Vercel in 5 minutes.

## Prerequisites

- GitHub account
- Vercel account (free) - https://vercel.com/signup
- Git installed on your computer

## Step 1: Prepare Your GitHub Repository

### If repository doesn't exist yet:

```bash
# Navigate to webapp directory
cd /Users/notodyss/Desktop/alihanbot/webapp

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Exchange Bot Mini App"

# Add remote
git remote add origin https://github.com/notOdyss/alihanminiapp.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### If repository already exists:

```bash
cd /Users/notodyss/Desktop/alihanbot/webapp

# Add all changes
git add .

# Commit
git commit -m "Add Vercel deployment configuration"

# Push
git push
```

## Step 2: Deploy to Vercel

### Option A: Using Vercel Dashboard (Easiest)

1. **Go to Vercel**: https://vercel.com/new

2. **Import Repository**:
   - Click "Import Git Repository"
   - Select "GitHub"
   - Search for: `notOdyss/alihanminiapp`
   - Click "Import"

3. **Configure Project**:
   ```
   Project Name: alihanminiapp (or your choice)
   Framework Preset: Vite (should auto-detect)
   Root Directory: ./ (leave as default)
   ```

4. **Build Settings** (should auto-fill):
   ```
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

5. **Environment Variables** (Optional for now):
   - Skip for now, we'll add later
   - Click "Deploy"

6. **Wait for deployment** (usually 1-2 minutes)

7. **Your app is live!** 🎉
   - You'll get a URL like: `https://alihanminiapp.vercel.app`
   - Copy this URL for next steps

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI globally
npm i -g vercel

# Navigate to webapp directory
cd /Users/notodyss/Desktop/alihanbot/webapp

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Step 3: Configure Backend API URL

### If your backend is already deployed:

1. Go to Vercel Dashboard
2. Select your project
3. Go to "Settings" → "Environment Variables"
4. Add variable:
   ```
   Name: VITE_API_URL
   Value: https://your-backend-api.com
   ```
5. Click "Save"
6. Go to "Deployments" tab
7. Click "..." on latest deployment
8. Click "Redeploy"

### If testing without backend:

The Mini App will work in demo mode without backend API.

## Step 4: Update Bot Configuration

### Update the bot to use your Vercel URL:

1. Open `bot/keyboards/main.py` on your local machine

2. Update this line:
```python
WEBAPP_URL = "https://alihanminiapp.vercel.app"  # Your Vercel URL
```

3. Restart your bot:
```bash
python3 -m bot.main
```

## Step 5: Register Mini App with BotFather

1. Open Telegram and message @BotFather

2. Send these commands:
```
/setmenubutton
@your_bot_username
https://alihanminiapp.vercel.app
```

3. Test by opening your bot and pressing the menu button

## Step 6: Test Your Mini App

1. Open your bot in Telegram
2. Click the menu button (bottom left)
3. Mini App should open
4. Test all pages: Transactions, Calculator, Balance, Statistics, More

## Automatic Deployments

Every time you push to GitHub, Vercel will automatically deploy:

```bash
# Make changes to your code
git add .
git commit -m "Update Mini App design"
git push

# Vercel will automatically deploy!
# Check deployment status at https://vercel.com/dashboard
```

## Custom Domain (Optional)

1. Go to Vercel Dashboard → Your Project
2. Click "Settings" → "Domains"
3. Add your domain: `miniapp.yourdomain.com`
4. Follow DNS configuration instructions
5. Update bot configuration with new domain

## Troubleshooting

### Build Failed

Check Vercel deployment logs:
1. Go to Vercel Dashboard
2. Click on failed deployment
3. View logs to see error
4. Common issues:
   - Missing dependencies: Run `npm install` locally
   - Build errors: Run `npm run build` locally to test

### Mini App Doesn't Load in Telegram

1. **Check HTTPS**: Vercel URLs are always HTTPS ✓
2. **Check URL**: Make sure URL in bot matches Vercel URL exactly
3. **Clear Telegram cache**: Close and reopen Telegram
4. **Check browser console**: Open Mini App in desktop Telegram, press F12

### API Requests Failing

1. Check `VITE_API_URL` environment variable in Vercel
2. Make sure backend API is accessible
3. Check CORS settings on backend
4. Check Network tab in browser console (F12)

### White Screen

1. Check Vercel deployment logs
2. Try rebuilding: `npm run build` locally
3. Check for JavaScript errors in console
4. Verify all imports are correct

## Vercel Dashboard URLs

- **Main Dashboard**: https://vercel.com/dashboard
- **Project Settings**: https://vercel.com/your-username/alihanminiapp/settings
- **Deployments**: https://vercel.com/your-username/alihanminiapp/deployments
- **Environment Variables**: https://vercel.com/your-username/alihanminiapp/settings/environment-variables

## Files Required for Vercel

These files are already in your repository:

- ✅ `package.json` - Dependencies and scripts
- ✅ `vite.config.js` - Vite configuration
- ✅ `vercel.json` - Vercel deployment config
- ✅ `.gitignore` - Git ignore rules
- ✅ All source files in `src/`

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://api.yourdomain.com` |

Note: All Vite environment variables must start with `VITE_`

## What Happens on Each Push?

1. You push code to GitHub
2. Vercel detects the push
3. Vercel runs `npm install`
4. Vercel runs `npm run build`
5. Vercel deploys the `dist` folder
6. Your Mini App is updated (usually takes 1-2 minutes)

## Vercel Free Plan Limits

- ✅ 100 GB bandwidth/month
- ✅ Unlimited projects
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Automatic deployments
- ✅ More than enough for a Telegram Mini App!

## Need Help?

- Vercel Documentation: https://vercel.com/docs
- Vercel Discord: https://discord.gg/vercel
- Contact: @thxfortheslapali or @herr_leutenant

## Summary

```bash
# 1. Push to GitHub
cd webapp
git add .
git commit -m "Deploy to Vercel"
git push

# 2. Import to Vercel
# Go to https://vercel.com/new
# Import: notOdyss/alihanminiapp

# 3. Update bot
# Edit: bot/keyboards/main.py
# Set: WEBAPP_URL = "https://alihanminiapp.vercel.app"

# 4. Register with BotFather
# /setmenubutton → URL

# Done! 🎉
```

Your Mini App is now live and will auto-deploy on every push!
