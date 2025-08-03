#!/bin/bash

# Bot monitoring and auto-restart script
# This script checks if the bot is running and restarts it if needed

BOT_DIR="/home/cheuer/telegram_bot_ai"
BOT_SCRIPT="bot.py"
LOGFILE="$BOT_DIR/bot_monitor.log"
PIDFILE="$BOT_DIR/bot.pid"
MAX_RESTARTS=5
RESTART_COUNT_FILE="$BOT_DIR/restart_count.txt"

# Function to log messages with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOGFILE"
}

# Function to get current restart count
get_restart_count() {
    if [ -f "$RESTART_COUNT_FILE" ]; then
        cat "$RESTART_COUNT_FILE"
    else
        echo "0"
    fi
}

# Function to increment restart count
increment_restart_count() {
    local count=$(get_restart_count)
    echo $((count + 1)) > "$RESTART_COUNT_FILE"
}

# Function to reset restart count (called when bot runs successfully for a while)
reset_restart_count() {
    echo "0" > "$RESTART_COUNT_FILE"
}

# Function to check if bot process is running
is_bot_running() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            # Check if it's actually our bot process
            if ps -p "$pid" -o cmd= | grep -q "$BOT_SCRIPT"; then
                return 0  # Bot is running
            fi
        fi
    fi
    return 1  # Bot is not running
}

# Function to start the bot
start_bot() {
    cd "$BOT_DIR"
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Start bot in background and save PID
    nohup python "$BOT_SCRIPT" > bot_output.log 2>&1 &
    echo $! > "$PIDFILE"
    
    log_message "Bot started with PID $(cat $PIDFILE)"
}

# Function to stop the bot
stop_bot() {
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            log_message "Bot stopped (PID: $pid)"
            sleep 2
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid"
                log_message "Bot force killed (PID: $pid)"
            fi
        fi
        rm -f "$PIDFILE"
    fi
}

# Function to check if bot is responsive (test Telegram API)
is_bot_responsive() {
    # Check if bot has been running for at least 30 seconds
    if [ -f "$PIDFILE" ]; then
        local pid=$(cat "$PIDFILE")
        local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null | xargs -I {} date -d "{}" +%s 2>/dev/null)
        local current_time=$(date +%s)
        
        if [ -n "$start_time" ] && [ $((current_time - start_time)) -lt 30 ]; then
            return 0  # Too early to test responsiveness
        fi
    fi
    
    # Check if there are recent errors in the log
    if [ -f "$BOT_DIR/bot_output.log" ]; then
        # Look for critical errors in the last 10 lines
        if tail -10 "$BOT_DIR/bot_output.log" | grep -qi "error\|exception\|failed\|traceback"; then
            return 1  # Bot seems to have errors
        fi
    fi
    
    return 0  # Bot seems responsive
}

# Main monitoring logic
main() {
    log_message "Starting bot monitor check"
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOGFILE")"
    
    # Check if we've reached max restarts
    local restart_count=$(get_restart_count)
    if [ "$restart_count" -ge "$MAX_RESTARTS" ]; then
        log_message "ERROR: Maximum restart attempts ($MAX_RESTARTS) reached. Manual intervention required."
        exit 1
    fi
    
    if is_bot_running; then
        if is_bot_responsive; then
            log_message "Bot is running and responsive"
            # Reset restart count if bot has been running fine
            reset_restart_count
        else
            log_message "Bot is running but not responsive, restarting..."
            stop_bot
            sleep 5
            increment_restart_count
            start_bot
        fi
    else
        log_message "Bot is not running, starting..."
        increment_restart_count
        start_bot
    fi
    
    log_message "Monitor check completed"
}

# Handle script arguments
case "$1" in
    start)
        log_message "Manual start requested"
        stop_bot
        reset_restart_count
        start_bot
        ;;
    stop)
        log_message "Manual stop requested"
        stop_bot
        ;;
    restart)
        log_message "Manual restart requested"
        stop_bot
        sleep 2
        reset_restart_count
        start_bot
        ;;
    status)
        if is_bot_running; then
            echo "Bot is running (PID: $(cat $PIDFILE 2>/dev/null))"
            echo "Restart count: $(get_restart_count)"
        else
            echo "Bot is not running"
        fi
        ;;
    *)
        # Default monitoring behavior (called by cron)
        main
        ;;
esac
