#!/bin/bash

# Log rotation script to prevent logs from growing too large
# Run this weekly via cron

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAX_SIZE=10485760  # 10MB in bytes

rotate_log() {
    local logfile="$1"
    local max_size="$2"
    
    if [ -f "$logfile" ]; then
        local size=$(stat -c%s "$logfile" 2>/dev/null || stat -f%z "$logfile" 2>/dev/null)
        if [ "$size" -gt "$max_size" ]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Rotating $logfile (size: $size bytes)"
            
            # Keep last 5 rotated logs
            for i in {4..1}; do
                if [ -f "${logfile}.$i" ]; then
                    mv "${logfile}.$i" "${logfile}.$((i+1))"
                fi
            done
            
            # Move current log to .1
            mv "$logfile" "${logfile}.1"
            
            # Create new empty log
            touch "$logfile"
            
            # Clean up old logs (keep only 5)
            for i in {6..10}; do
                if [ -f "${logfile}.$i" ]; then
                    rm "${logfile}.$i"
                fi
            done
        fi
    fi
}

# Rotate logs if they exceed size limit
rotate_log "$BOT_DIR/bot_output.log" $MAX_SIZE
rotate_log "$BOT_DIR/bot_monitor.log" $MAX_SIZE
rotate_log "$BOT_DIR/logs/cron.log" $MAX_SIZE

# Clean up old temporary files
find "$BOT_DIR" -name "*.tmp" -mtime +7 -delete 2>/dev/null || true

echo "$(date '+%Y-%m-%d %H:%M:%S') - Log rotation completed"
