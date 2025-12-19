#!/bin/bash

# Script to push Mini App to GitHub
# Repository: https://github.com/notOdyss/alihanminiapp.git

echo "📦 Pushing to GitHub: notOdyss/alihanminiapp"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found!"
    echo "Please run this script from the webapp directory"
    exit 1
fi

echo "✅ In webapp directory"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📂 Initializing git repository..."
    git init
    echo "✅ Git initialized"
    echo ""
fi

# Check if remote exists
if ! git remote | grep -q "origin"; then
    echo "🔗 Adding remote repository..."
    git remote add origin https://github.com/notOdyss/alihanminiapp.git
    echo "✅ Remote added"
    echo ""
else
    echo "✅ Remote already configured"
    echo ""
fi

# Show current status
echo "📋 Current status:"
git status --short
echo ""

# Add all files
echo "➕ Adding all files..."
git add .
echo "✅ Files added"
echo ""

# Prompt for commit message
echo "💬 Enter commit message (or press Enter for default):"
read -r commit_message

if [ -z "$commit_message" ]; then
    commit_message="Update Mini App - $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Commit
echo "💾 Committing changes..."
git commit -m "$commit_message"
echo "✅ Changes committed"
echo ""

# Get current branch
current_branch=$(git branch --show-current)

if [ -z "$current_branch" ]; then
    current_branch="main"
    git branch -M main
    echo "✅ Set branch to main"
    echo ""
fi

# Push to GitHub
echo "🚀 Pushing to GitHub..."
echo "Branch: $current_branch"
echo ""

if git push -u origin "$current_branch" 2>&1; then
    echo ""
    echo "============================================"
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🔗 Repository: https://github.com/notOdyss/alihanminiapp"
    echo "🌿 Branch: $current_branch"
    echo "💬 Commit: $commit_message"
    echo ""
    echo "📚 Next steps:"
    echo "1. Go to https://vercel.com/new"
    echo "2. Import your repository"
    echo "3. Deploy!"
    echo ""
    echo "Or run: vercel --prod"
    echo ""
else
    echo ""
    echo "============================================"
    echo "⚠️  Push failed! Common issues:"
    echo ""
    echo "1. Authentication failed:"
    echo "   - Generate Personal Access Token on GitHub"
    echo "   - Use token as password when prompted"
    echo ""
    echo "2. Repository not empty:"
    echo "   - Run: git pull origin main --allow-unrelated-histories"
    echo "   - Then run this script again"
    echo ""
    echo "3. Need to force push:"
    echo "   - Run: git push -u origin main --force"
    echo "   - (Warning: This will overwrite remote)"
    echo ""
    exit 1
fi
