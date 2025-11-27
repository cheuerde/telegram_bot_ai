#!/bin/bash
#
# Deploy Telegram Bot AI to VM
#
# This script:
# 1. Syncs code to VM via git
# 2. Installs systemd service
# 3. Removes old cron-based monitoring
# 4. Starts the bot
#
# Usage: ./deploy.sh
#

set -e

VM_HOST="VM"  # From ~/.ssh/config
BOT_DIR="/home/cheuer/telegram_bot_ai"

echo "=========================================="
echo "Telegram Bot AI - Deployment"
echo "=========================================="

# Step 1: Commit and push local changes
echo ""
echo "[1/5] Committing and pushing local changes..."
git add -A
git commit -m "Robust bot with systemd support" || echo "Nothing to commit"
git push origin main

# Step 2: Pull changes on VM
echo ""
echo "[2/5] Pulling changes on VM..."
ssh $VM_HOST "cd $BOT_DIR && git fetch origin main && git reset --hard origin/main"

# Step 3: Update .env file format for systemd
echo ""
echo "[3/5] Updating environment file for systemd..."
ssh $VM_HOST "cat > $BOT_DIR/.env << 'ENVEOF'
# Telegram Bot AI - Environment Variables
# This file is read by systemd (no 'export' keyword needed)

TELEGRAM_API_KEY=\$(grep -oP 'TELEGRAM_API_KEY=\K.*' $BOT_DIR/.env.backup 2>/dev/null || echo 'YOUR_KEY_HERE')
OPENAI_API_KEY=\$(grep -oP 'OPENAI_API_KEY=\K.*' $BOT_DIR/.env.backup 2>/dev/null || echo 'YOUR_KEY_HERE')

# Path settings
PATH=/usr/local/bin:/usr/bin:/bin
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8
ENVEOF"

# Actually, let's preserve the existing keys
ssh $VM_HOST "cd $BOT_DIR && \
    if [ -f .env ]; then \
        cp .env .env.backup; \
        TGKEY=\$(grep 'TELEGRAM_API_KEY' .env.backup | grep -oP '(?<==).*' | tr -d '\"' | head -1); \
        OAKEY=\$(grep 'OPENAI_API_KEY' .env.backup | grep -oP '(?<==).*' | tr -d '\"' | head -1); \
        cat > .env << EOF
# Telegram Bot AI - Environment Variables
TELEGRAM_API_KEY=\$TGKEY
OPENAI_API_KEY=\$OAKEY
PATH=/usr/local/bin:/usr/bin:/bin
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8
EOF
    fi"

# Step 4: Install systemd service
echo ""
echo "[4/5] Installing systemd service..."
ssh $VM_HOST "sudo cp $BOT_DIR/telegram-bot.service /etc/systemd/system/ && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable telegram-bot.service"

# Step 5: Remove old cron job and start service
echo ""
echo "[5/5] Removing old cron monitoring and starting service..."

# Remove old cron job
ssh $VM_HOST "crontab -l 2>/dev/null | grep -v 'telegram_bot_ai/monitor_bot.sh' | crontab - || true"

# Stop any running bot processes
ssh $VM_HOST "cd $BOT_DIR && ./monitor_bot.sh stop 2>/dev/null || true"
ssh $VM_HOST "pkill -f 'python.*bot.py' 2>/dev/null || true"

# Reset restart count
ssh $VM_HOST "echo 0 > $BOT_DIR/restart_count.txt 2>/dev/null || true"

# Start the systemd service
ssh $VM_HOST "sudo systemctl restart telegram-bot.service"

# Check status
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
ssh $VM_HOST "sudo systemctl status telegram-bot.service --no-pager"
echo ""
echo "Useful commands:"
echo "  ssh VM 'sudo systemctl status telegram-bot'   # Check status"
echo "  ssh VM 'sudo journalctl -u telegram-bot -f'   # View live logs"
echo "  ssh VM 'sudo systemctl restart telegram-bot'  # Restart"
echo "  ssh VM 'sudo systemctl stop telegram-bot'     # Stop"

