#!/bin/bash
# Process manager for Clawdbot
# This script keeps the bot running in the background

BOT_SCRIPT="live_clawdbot_bot.py"
PID_FILE="/tmp/clawdbot.pid"
LOG_FILE="logs/clawdbot.log"

start() {
    if [ -f "$PID_FILE" ]; then
        echo "Bot is already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    mkdir -p logs
    nohup python3 "$BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Bot started (PID: $(cat $PID_FILE))"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Bot is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    kill $PID
    rm "$PID_FILE"
    echo "Bot stopped"
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "Bot is running (PID: $PID)"
            return 0
        else
            echo "Bot is not running (stale PID file)"
            rm "$PID_FILE"
            return 1
        fi
    else
        echo "Bot is not running"
        return 1
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
