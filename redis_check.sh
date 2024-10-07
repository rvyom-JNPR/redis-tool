#!/bin/bash

# Configuration
#REDIS_HOST="redis-lisatest.vtgldn.clustercfg.use1.cache.amazonaws.com"
REDIS_HOST="vyomtest.vtgldn.clustercfg.use1.cache.amazonaws.com"
REDIS_PORT=6379
DURATION=1800  # Test duration in seconds (30 minutes)
INTERVAL=1     # Interval between commands in seconds

# Variables to track downtime
total_downtime=0
downtime_start=0
start_test_time=$(date +%s)

# Function to get current time in a readable format
current_time() {
    date +"%Y-%m-%d %H:%M:%S"
}

# Start the testing loop
end_time=$((start_test_time + DURATION))
while [[ $(date +%s) -lt $end_time ]]; do
    now=$(current_time)

    # Attempt to set a key and get the value
    redis-cli -c -h "$REDIS_HOST" -p "$REDIS_PORT" set foo bar > /dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        # Handle connection errors
        if [[ $downtime_start -eq 0 ]]; then
            downtime_start=$(date +%s)  # Start counting downtime
            echo "$now - Redis connection failed. Downtime started."
        fi
    else
        # If Redis is reachable
        if [[ $downtime_start -ne 0 ]]; then
            downtime_duration=$(( $(date +%s) - downtime_start ))
            total_downtime=$((total_downtime + downtime_duration))
            echo "$now - Redis is reachable again. Downtime ended: $downtime_duration seconds."
            downtime_start=0  # Reset downtime tracking
        fi

        # Get the value
        x=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" get foo 2>/dev/null)
        echo "$now - Value retrieved: ${x:-None}"
    fi

    # Wait before the next command
    sleep $INTERVAL
done

# Final report
if [[ $downtime_start -ne 0 ]]; then
    downtime_duration=$(( $(date +%s) - downtime_start ))
    total_downtime=$((total_downtime + downtime_duration))
    echo "$(current_time) - Redis was NOT reachable at the end of the test. Additional downtime: $downtime_duration seconds."
fi

# Calculate total elapsed time
total_elapsed_time=$(( $(date +%s) - start_test_time ))
echo "$(current_time) - Total downtime during the test: $total_downtime seconds."
echo "$(current_time) - Total elapsed time of the test: $total_elapsed_time seconds."
