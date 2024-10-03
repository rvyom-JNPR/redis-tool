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

# Capture the start time of the test
start_test_time = time.time()

# Function to get current time in a readable format
def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# Start the testing loop
end_time = start_test_time + DURATION
while time.time() < end_time:
    # Get current time at the start of each iteration
    now = current_time()
    
    try:
        # Initialize Redis cluster client
        rc = RedisCluster(host=REDIS_HOST, port=REDIS_PORT)

        # Attempt to set a key
        rc.set('foo', 'bar')

        # Start timing to check response
        start_time = time.time()
        
        # Attempt to get the value
        x = rc.get('foo')

        # Calculate the response time
        response_time = time.time() - start_time

        # Check if the response is received within the timeout
        if response_time > TIMEOUT:
            # If the response takes too long, it's downtime
            if downtime_start is None:
                downtime_start = time.time()  # Start counting downtime
                print(f"{now} - Redis is NOT reachable. Downtime started.")
            continue  # Skip the rest of the loop

        # Reset downtime tracking if the response is received in time
        if downtime_start is not None:
            downtime_duration = time.time() - downtime_start
            total_downtime += downtime_duration
            downtime_start = None  # Reset downtime start time
            print(f"{now} - Redis is reachable. Downtime ended: {downtime_duration:.2f} seconds.")
        
        # Print the response
        print(f"{now} - Value retrieved: {x.decode('utf-8') if x else 'None'}, Response time: {response_time:.4f} seconds")

    except (ConnectionError, Exception) as e:
        # Handle any connection errors or other exceptions
        if downtime_start is None:
            downtime_start = time.time()  # Start counting downtime
            print(f"{now} - Redis is NOT reachable. Downtime started.")
        
        # Optional: Log the error message
        print(f"{now} - An error occurred: {e}. Reinitializing connection.")

        # Optionally add a delay before the next connection attempt
        time.sleep(INTERVAL)

    # Wait before the next command
    time.sleep(INTERVAL)

# Final report
if downtime_start is not None:
    # If we were in a downtime state at the end of the test
    downtime_duration = time.time() - downtime_start
    total_downtime += downtime_duration
    print(f"{now} - Redis is NOT reachable at the end of the test. Additional downtime: {downtime_duration:.2f} seconds.")

# Calculate total elapsed time
total_elapsed_time = time.time() - start_test_time
print(f"{now} - Total downtime during the test: {total_downtime:.2f} seconds.")
print(f"{now} - Total elapsed time of the test: {total_elapsed_time:.2f} seconds.")
