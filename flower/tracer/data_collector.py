import sys
import json
import re
from datetime import datetime

from redis_lib import redis_wrapped_api

"""
How to trace the data: parameters

@params:
	1. Trace by provider name
	2. Trace by task date
	3. Trace by task name
	4. Trace by task status
	5. View different type of task exceptions

	@attributes of result:
	1. Provider
	2. Task name
	3. Task processed time
	4. Result
	5. Exception Type
	6. Exception message
	7. Args
	8. Kwargs
	9. Queue name
	10. origin
	11. Worker hostname
"""


KEY_PATTERN = "dist_it:result:#DATE*#PROVIDER_NAME*#TASK_NAME*"
WILD_CARD = "*"

class RedisTask(object):
	def __init__(self):
		pass

class Patttern(object):
	def __init__(self, pname, tname, tdate):
		self._provider_name = pname
		self._task_name = tname
		self._task_date = tdate

	def get_redis_key_pattern(self):

		with open ("F:\celery_logs\log_tracer.txt","a") as f:
			f.write("\n"+str(self._get_internal_pattern()))

		return self._get_internal_pattern()

	def _get_formatted_date(self, str_task_date=None):
		if str_task_date is None:
			raise ValueError("The task date is invalid.")

		task_datetime = datetime.strptime(self._task_date, "%Y-%m-%d")
		return str(task_datetime.strftime("%y%m%d"))

	def _get_internal_pattern(self):
		p = KEY_PATTERN

		if self._is_param_valid(self._task_date):
			p = re.sub("#DATE", self._get_formatted_date(self._task_date), p)
		else:
			p = re.sub("#DATE", WILD_CARD, p)

		if self._is_param_valid(self._provider_name):
			p = re.sub("#PROVIDER_NAME", self._provider_name, p)
		else:
			p = re.sub("#PROVIDER_NAME", WILD_CARD, p)

		if self._is_param_valid(self._task_name):
			p = re.sub("#TASK_NAME", self._task_name, p)
		else:
			p = re.sub("#TASK_NAME", WILD_CARD, p)

		return p

	def _is_param_valid(self, param):
		if param is None or not isinstance(param, str) or len(param) == 0:
			return False

		return True

class DataTracer(object):

	def __init__(self):
		pass

	@staticmethod
	def get_all_data_for_pattern(cursor_pos = 0, pattern = None):
		if pattern is None:
			raise ValueError("None pattern can't be used")

		wrapper_api_instance = redis_wrapped_api.RedisWrappedApi()
		cursor, data_with_pattern = wrapper_api_instance.get_all_key_value_with_pattern_and_max_count(cursor_pos, pattern, 50)
		result_data = list()

		for key, value in data_with_pattern.items():	
			# print key, value		
			result_item = dict()
			json_data = json.loads(value)

			result_item["UUID"] = key
			result_item["provider_name"] = key.split(':')[3].split('.')[0]
			result_item["task_id"] = json_data["task_id"]
			result_item["task_status"] = json_data["status"]
			
			result_item["error"] = dict()
			result_item["error"]["traceback"] = json_data["traceback"]
			result_item["error"]["exception_message"] = ""
			result_item["error"]["exception_type"] = ""
			result_item['result'] = ""
			result_item["error"]["exception_message"] = ""
			result_item["error"]["exception_type"] = ""
			result_item["origin"] = ""
			result_item["args"] = ""
			result_item["kwargsrepr"] = ""
			result_item["task_name"] = ""
			result_item["queue"] = ""
			result_item["worker_host"] = ""
			result_item["processed_at"] = ""

			if "processed_at" in json_data:
				result_item["processed_at"] = json_data["processed_at"]

			if json_data["result"] is not None:
				result_item['result'] = json_data["result"]
				if json_data["result"]["exc_message"] is not None:
					result_item["error"]["exception_message"] = json_data["result"]["exc_message"]

				if json_data["result"]["exc_type"] is not None:
					result_item["error"]["exception_type"] = json_data["result"]["exc_type"]

			if "request" in json_data and json_data["request"] is not None:
				request_dict = json_data["request"]

				if request_dict is not None and len(request_dict) > 0:
					if "origin" in request_dict:
						result_item["origin"] = request_dict["origin"]
					if "args" in request_dict:
						result_item["args"] = request_dict["args"]
					if "kwargsrepr" in request_dict:
						result_item["kwargsrepr"] = request_dict["kwargsrepr"]
					if "task" in request_dict:
						result_item["task_name"] = request_dict["task"]
					if "delivery_info" in request_dict and request_dict["delivery_info"] is not None and "routing_key" in request_dict["delivery_info"]:
						result_item["queue"] = request_dict["delivery_info"]["routing_key"]
					if "hostname" in request_dict:
						result_item["worker_host"] = request_dict["hostname"]

			result_data.append(result_item)

		return cursor, result_data

	@staticmethod
	def get_all_data_for_pattern_iter(pattern = None):
		if pattern is None:
			raise ValueError("None pattern can't be used")

		wrapper_api_instance = redis_wrapped_api.RedisWrappedApi()
		data_with_pattern = wrapper_api_instance.get_all_key_value_with_pattern_iter(pattern)
		result_data = list()

		for key, value in data_with_pattern.items():	
			# print key, value		
			result_item = dict()
			json_data = json.loads(value)

			result_item["UUID"] = key
			result_item["provider_name"] = key.split(':')[3].split('.')[0]
			result_item["task_id"] = json_data["task_id"]
			result_item["task_status"] = json_data["status"]
			
			result_item["error"] = dict()
			result_item["error"]["traceback"] = json_data["traceback"]
			result_item["error"]["exception_message"] = ""
			result_item["error"]["exception_type"] = ""
			result_item['result'] = ""
			result_item["error"]["exception_message"] = ""
			result_item["error"]["exception_type"] = ""
			result_item["origin"] = ""
			result_item["args"] = ""
			result_item["kwargsrepr"] = ""
			result_item["task_name"] = ""
			result_item["queue"] = ""
			result_item["worker_host"] = ""
			result_item["processed_at"] = ""

			if "processed_at" in json_data:
				result_item["processed_at"] = json_data["processed_at"]

			if json_data["result"] is not None:
				result_item['result'] = json_data["result"]
				if json_data["result"]["exc_message"] is not None:
					result_item["error"]["exception_message"] = json_data["result"]["exc_message"]

				if json_data["result"]["exc_type"] is not None:
					result_item["error"]["exception_type"] = json_data["result"]["exc_type"]

			if "request" in json_data and json_data["request"] is not None:
				request_dict = json_data["request"]

				if request_dict is not None and len(request_dict) > 0:
					if "origin" in request_dict:
						result_item["origin"] = request_dict["origin"]
					if "args" in request_dict:
						result_item["args"] = request_dict["args"]
					if "kwargsrepr" in request_dict:
						result_item["kwargsrepr"] = request_dict["kwargsrepr"]
					if "task" in request_dict:
						result_item["task_name"] = request_dict["task"]
					if "delivery_info" in request_dict and request_dict["delivery_info"] is not None and "routing_key" in request_dict["delivery_info"]:
						result_item["queue"] = request_dict["delivery_info"]["routing_key"]
					if "hostname" in request_dict:
						result_item["worker_host"] = request_dict["hostname"]

			result_data.append(result_item)

		return result_data

	def get_data_by_provider(self, pattern = None):
		pass

	def get_data_by_task(self, pattern = None):
		pass

	def get_data_by_date(self, pattern = None):
		pass

	@staticmethod
	def get_task_by_id(task_id):
		wrapper_api_instance = redis_wrapped_api.RedisWrappedApi()
		data = wrapper_api_instance.get_task_details(task_id)
		task_data = json.loads(json.loads(data))

		task = RedisTask()
		task.task_name = task_data['request']['task']
		task.uuid = task_data['task_id']
		task.state = task_data['status']
		task.args = task_data['request']['args']
		task.kwargs = task_data['request']['kwargsrepr']
		task.result = task_data['result']
		
		task.exception_type = ''
		if 'result' in task_data and task_data['result'] is not None and 'exc_type' in task_data['result']:
			task.exception_type = task_data['result']['exc_type']

		task.exception_message = ''
		if 'result' in task_data and task_data['result'] is not None and 'exc_message' in task_data['result']:
			task.exception_message = task_data['result']['exc_message']

		task.processed_at = task_data['processed_at']
		task.traceback = task_data['traceback']
		task.origin = task_data['request']['origin']
		task.type = task_data['request']['task']
		task.queue = task_data['request']['delivery_info']['routing_key']
		task.worker = task_data['request']['hostname']

		return task

	@staticmethod
	def sort_on_processed_time(task_list = []):
		return sorted(task_list, DataTracer.compare)

	@staticmethod
	def compare(task1, task2):
		task1_processed = datetime.strptime(task1['processed_at'], "%Y-%m-%d %H:%M:%S.%f")
		task2_processed = datetime.strptime(task2['processed_at'], "%Y-%m-%d %H:%M:%S.%f")

		if task1_processed > task2_processed:
			return -1
		elif task1_processed < task2_processed:
			return 1
		
		return 0

if __name__ == "__main__":
	# pattern = "dist_it:result*bitla.*"
	# print DataTracer.get_all_data_for_pattern(pattern)

	task_obj = DataTracer.get_task_by_id("dist_it:result:170125:bitla.pull_n_process_search:40-11-53-00")
	print repr(task_obj)