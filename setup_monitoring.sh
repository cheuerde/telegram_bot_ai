#!/bin/bash

# Setup script for bot monitoring system

BOT_DIR="/home/cheuer/telegram_bot_ai"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up bot monitoring system..."

# Make scripts executable
chmod +x "$SCRIPT_DIR/monitor_bot.sh"
chmod +x "$SCRIPT_DIR/run_app.sh"
chmod +x "$SCRIPT_DIR/set_uv_env.sh"

# Update the BOT_DIR in monitor_bot.sh to current directory
sed -i "s|BOT_DIR=\"/home/cheuer/telegram_bot_ai\"|BOT_DIR=\"$SCRIPT_DIR\"|g" "$SCRIPT_DIR/monitor_bot.sh"

echo "Creating log directory..."
mkdir -p "$SCRIPT_DIR/logs"

# Create a crontab entry (user will need to install it manually)
CRON_ENTRY="*/2 * * * * $SCRIPT_DIR/monitor_bot.sh >> $SCRIPT_DIR/logs/cron.log 2>&1"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Manual steps required:"
echo ""
echo "1. Add this cron job to monitor the bot every 2 minutes:"
echo "   Run: crontab -e"
echo "   Add this line:"
echo "   $CRON_ENTRY"
echo ""
echo "2. Start the bot monitoring:"
echo "   $SCRIPT_DIR/monitor_bot.sh start"
echo ""
echo "🎛️  Available commands:"
echo "   $SCRIPT_DIR/monitor_bot.sh start    - Start the bot"
echo "   $SCRIPT_DIR/monitor_bot.sh stop     - Stop the bot"
echo "   $SCRIPT_DIR/monitor_bot.sh restart  - Restart the bot"
echo "   $SCRIPT_DIR/monitor_bot.sh status   - Check bot status"
echo ""
echo "📊 Monitor logs:"
echo "   Bot logs: $SCRIPT_DIR/bot_output.log"
echo "   Monitor logs: $SCRIPT_DIR/bot_monitor.log"
echo "   Cron logs: $SCRIPT_DIR/logs/cron.log"
echo ""
