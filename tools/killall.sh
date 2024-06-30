#!/bin/bash

# Find the PID of the process running python aihbot.py on ttys007
PID=$(ps aux | grep 'aihbot' | grep -v 'grep' | awk '{print $2}')

# Check if PID is not empty
if [ -z "$PID" ]; then
    echo "No process found for 'python aihbot.py' on ttys007"
else
    # Kill the process
    kill -9 $PID
    echo "Killed process with PID: $PID"
fi

