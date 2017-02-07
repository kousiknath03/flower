import sys
import redis_connection
import json

class RedisWrappedApi(object):
	def __init__(self, redis_client = None):
		self._client = redis_connection.get_redis_client()

	def get_all_key_value_with_pattern(self, cursor_pos = 0, pattern = None):
		"""
		This is wrapper implementation of redis library which doesn't care about any key. 
		The application should care about what pattern to send to the wrapper.
		"""
		
		cursor, redis_data = self._client.scan(cursor=cursor_pos, match = pattern, count=50)
		result_data = dict()

		for key in redis_data:
			result_data[key] = self.get_string(key)

		return cursor, result_data

	def get_all_key_value_with_pattern_iter(self, pattern = None):
		"""
		This is wrapper implementation of redis library which doesn't care about any key. 
		The application should care about what pattern to send to the wrapper.
		"""
		
		redis_data = self._client.scan_iter(match = pattern, count=50)
		result_data = dict()

		for key in redis_data:
			result_data[key] = self.get_string(key)

		return result_data

	def get_all_key_value_with_pattern_and_max_count(self, cursor = 0, pattern=None, total_result_count = 10):
		cursor, redis_data = self._scan_iter_with_cursor(cursor, pattern, total_result_count)
		result_data = dict()

		for key in redis_data:
			result_data[key] = self.get_string(key)

		if cursor == 0 or cursor == '0':
			cursor = None

		return cursor, result_data

	def _scan_iter_with_cursor(self, cursor = 0, match=None, result_item_count=10):
		"""
		result item count is not equal to redis result count.
		result item count is total item count that the user expects.
		redis scan iter count is that count which is approximate result count that redis returns.
		"""
		list_result = list()
		redis_result_count = 100 # need to be configurable.

		while len(list_result) <= result_item_count:
			cursor, data = self._client.scan(cursor=cursor, match=match, count=redis_result_count)
			for item in data:
				list_result.append(item)

			if cursor == 0:
				break

		return cursor, list_result

	def get_string(self, key=None):
		if key is None:
			raise ValueError("None key is invalid.")

		return self._client.get(key)

	def get_task_details(self, task_id=None):
		if task_id is None:
			raise ValueError("Can't retrieve any task for None task id.")

		task_data = self._client.get(task_id)
		return json.dumps(task_data)

def test():
	p = "dist_it:result*bitla.*"
	api = RedisWrappedApi()

	c, all_key_value = api.get_all_key_value_with_pattern(0, p)

	print all_key_value

if __name__ == "__main__":
	test()