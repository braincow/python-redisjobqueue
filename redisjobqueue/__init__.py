import redis
import redlock
import time
import datetime
import json

class JobLockHasExpiredException(Exception):
	"""This Exception is raised when access or modify is attempted on a job that had its lock expire"""
	pass

class JobNotValidException(Exception):
	"""This Exception is raised when access or modify is attempted on a job that was previously already completed"""
	pass

class JobAlreadyInQueueException(Exception):
	"""This Exception is raised if adding a duplicate job to a queue is detected and therefore refused."""
	pass

class RedisJobQueueItem(object):
	def __init__(self, data, lock, queue):
		"""Job item in work queue"""
		# store job info for later use
		self.data = data
		self.lock = lock
		self.queue = queue
		# on init this job becomes valid as it has a lock
		self.valid = True
		# and also calculate the datetime in UTC after which the lock expires
		self.expires = datetime.datetime.utcnow() + datetime.timedelta(milliseconds=self.lock.validity)

	def _isvalid(self):
		# check for internal status flag
		if not self.valid:
			raise JobNotValidException("This job has been released previously.")
		# check for job lock validity
		if datetime.datetime.utcnow() > self.expires:
			raise JobLockHasExpiredException("Lock for this job has expired.")

		# always return true if no exception on validity checks were raised
		return True

	def get(self):
		"""Fetch the data stored in this job"""
		if self._isvalid():
			return self.data

	def complete(self):
		"""Delete job from queue and release the lock"""
		if self._isvalid():
			# delete item from queue
			self.queue.rem(self.data)
			# release lock after removal or failure
			self.queue.dlm.unlock(self.lock)
			# mark job as invalid
			self.valid = False

	def release(self):
		"""Release lock only and leave data in queue"""
		if self._isvalid():
			# mark job as invalid
			self.valid = False
			# release lock
			self.queue.dlm.unlock(self.lock)

class RedisJobQueue(object):
	def __init__(self, name, redis_host="localhost", redis_port=6379, namespace="queue"):
		"""Simple message queue with Redis backend and distributed locking"""
		# construct queue namespace
		self.key = "%s:%s" % (namespace, name)
		# @FIXME: this is ugly, make this whole constructor play nice with Redis and Redlock to provide
		#  access to clusters etc.
		conn_params = [{"host": redis_host, "port": redis_port, "db": 0}, ]
		# try to open redis connection to host
		self.redis = redis.Redis(redis_host, redis_port)
		# also open a lock redis connection to host
		self.dlm = redlock.Redlock(conn_params)

	def size(self):
		"""Return the approximate size of the queue."""
		return self.redis.zcard(self.key)

	def put(self, item):
		"""Put item into the queue."""
		# use current seconds from epoc moment as a score for Redis ZADD to accomplished sorted fifo queue
		if not self.redis.zadd(self.key, json.dumps(item), time.time()):
			raise JobAlreadyInQueueException("This job was found in Redis based work queue '%s'. Refusing to add it." % self.key)

	def get(self, lock_timeout = 1000):
		"""Get a job from the list if available and lock it"""
		# get the members in the list and try to acquire a lock until succesful
		for item in self.redis.zrange(self.key, 0, -1):
			my_lock = self.dlm.lock(item, lock_timeout)
			if my_lock:
				# exit here because we found and locked a job
				return RedisJobQueueItem(json.loads(item), my_lock, self)

	def rem(self, item):
		"""Remove item from job queue"""
		if not self.redis.zrem(self.key, json.dumps(item)):
			raise JobNotValidException("This job was not found in Redis workqueue.")

# eof