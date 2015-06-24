# python-redisjobqueue
Non-blocking job queue for Redis backend with distributed locking mechanism to allow safely multiple processes or threads asynchronously get jobs to process.

This software was originally written at [Eniram ltd](http://www.eniram.fi) in summer of 2015 and open sourced in the hope that it will benefit others as well.

## How-To use

### Queue consumer -- get job from queue and lock it

Import the library to your project:
```python
from redisjobqueue import RedisJobQueue
# we also require time functions in this example later on
import time
```

Initialize queue and connection to Redis server:
```python
# redis server hostname and port number are optional arguments
#  and defaults are show below
queue = RedisJobQueue("my-queue", "redis-host", 6379)
```

Create a simple loop to wait for a job to appear in the queue:
```python
while True:
	# sleep a second before querying for a new job
	time.sleep(1)
	# lock_timeout is in milliseconds the amount of time after which lock
	#  automatically expires and the job is considered available for other
	#  consumers as well. Default is shown below.
	job = queue.get(lock_timeout=1000)
	if job:
		job_payload = job.get()
		print job_payload
		# release lock and remove data from queue
		job.complete()
```

### Queue publisher -- add work to queue

Import the library to your project:
```python
from redisjobqueue import RedisJobQueue
```

Initialize queue and connection to Redis server:
```python
# redis server hostname and port number are optional arguments
#  and defaults are show below
queue = RedisJobQueue("my-queue", "redis-host", 6379)
```
Push new jobs to the queue:
```python
for i in range(10):
	# here we push a simple string to the queue but almost any datastructure is
	#  acceptable as long as it json serializable
	job_payload = "Hello world %i!" % i
	queue.put(job_payload)
```
