import time
from redis.cluster import RedisCluster
from redis.exceptions import ConnectionError

# Configuration
REDIS_HOST = "redis-lisatest.vtgldn.clustercfg.use1.cache.amazonaws.com"
REDIS_PORT = 6379
DURATION = 1800  # Test duration in seconds (30 minutes)
INTERVAL = 1     # Interval between commands in seconds
TIMEOUT = 1      # Timeout for getting a response in seconds

# Variables to track downtime
total_downtime = 0
downtime_start = None
last_successful_time = time.time()  # Track the last successful response time

# Capture the start time of the test
start_test_time = time.time()

# Function to get current time in a readable format
def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# Start the testing loop
end_time = start_test_time + DURATION
while time.time() < end_time:
    now = current_time()
    
    try:
        # Initialize Redis cluster client
        rc = RedisCluster(host=REDIS_HOST, port=REDIS_PORT)

        # Check if there's a large gap since the last successful connection
        if time.time() - last_successful_time > INTERVAL + 1:
            if downtime_start is None:
                downtime_start = last_successful_time
                print(f"{now} - Detected a gap in responses. Downtime started.")
            downtime_duration = time.time() - downtime_start
            total_downtime += downtime_duration
            print(f"{now} - Redis connection restored. Downtime lasted {downtime_duration:.2f} seconds.")
            downtime_start = None

        # Start timing to check response
        start_time = time.time()

        # Attempt to set a key
        rc.set('foo', 'bar')

        # Attempt to get the value
        x = rc.get('foo')

        # Calculate the response time
        response_time = time.time() - start_time

        # Check if the response time is slower than the timeout
        if response_time > TIMEOUT:
            if downtime_start is None:
                downtime_start = time.time()  # Start counting downtime
                print(f"{now} - Redis response too slow. Downtime started.")
        else:
            # If Redis is reachable within acceptable time
            if downtime_start is not None:
                downtime_duration = time.time() - downtime_start
                total_downtime += downtime_duration
                print(f"{now} - Redis is reachable again. Downtime ended: {downtime_duration:.2f} seconds.")
                downtime_start = None  # Reset downtime tracking

            # Print the successful response
            print(f"{now} - Value retrieved: {x.decode('utf-8') if x else 'None'}, Response time: {response_time:.4f} seconds")

        # Update the last successful time
        last_successful_time = time.time()

    except (ConnectionError, Exception) as e:
        # Handle connection errors or exceptions
        if downtime_start is None:
            downtime_start = time.time()  # Start counting downtime
            print(f"{now} - Redis connection failed. Downtime started.")
        
        # Log the error
        print(f"{now} - An error occurred: {e}. Reinitializing connection.")

    # Wait before the next command
    time.sleep(INTERVAL)

# Final report
if downtime_start is not None:
    # If downtime was ongoing at the end of the test, calculate it
    downtime_duration = time.time() - downtime_start
    total_downtime += downtime_duration
    print(f"{current_time()} - Redis was NOT reachable at the end of the test. Additional downtime: {downtime_duration:.2f} seconds.")

# Calculate total elapsed time
total_elapsed_time = time.time() - start_test_time
print(f"{current_time()} - Total downtime during the test: {total_downtime:.2f} seconds.")
print(f"{current_time()} - Total elapsed time of the test: {total_elapsed_time:.2f} seconds.")
