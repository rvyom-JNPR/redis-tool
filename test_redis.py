import redis
import time

# Configuration
REDIS_HOST = "redis-lisatest.vtgldn.clustercfg.use1.cache.amazonaws.com"
REDIS_PORT = 6379
DURATION = 900  # Test duration in seconds
INTERVAL = 1    # Interval between commands in seconds

# Initialize Redis client
client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

# Variables to track downtime
total_downtime = 0
downtime_start = None

# Start the testing loop
end_time = time.time() + DURATION
while time.time() < end_time:
    try:
        # Attempt to PING the Redis server
        response = client.ping()
        print("Able to ping to redis")
        if response:
            if downtime_start is not None:
                # Calculate the duration of downtime
                downtime_duration = time.time() - downtime_start
                total_downtime += downtime_duration
                downtime_start = None  # Reset downtime start time
                print(f"Redis is reachable. Downtime ended: {downtime_duration:.2f} seconds.")
        else:
            # This branch should not be reached since ping() raises an exception
            pass
    except (redis.ConnectionError, redis.TimeoutError):
        # Redis is not reachable
        if downtime_start is None:
            downtime_start = time.time()  # Start counting downtime
            print("Redis is NOT reachable. Downtime started.")

    # Wait before the next ping
    time.sleep(INTERVAL)

# Final report
if downtime_start is not None:
    # If we were in a downtime state at the end of the test
    total_downtime += time.time() - downtime_start
    print(f"Redis is NOT reachable at the end of the test. Additional downtime: {time.time() - downtime_start:.2f} seconds.")

print(f"Total downtime during the test: {total_downtime:.2f} seconds.")

