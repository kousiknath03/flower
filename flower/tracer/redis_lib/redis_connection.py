import redis

REDIS_HOST = "ec2-54-169-33-235.ap-southeast-1.compute.amazonaws.com"
REDIS_PASSWORD = "abcdef"
REDIS_PORT = 6379
REDIS_DB = 1

_redis_client=redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD, socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', unix_socket_path=None)				

def get_redis_client():
	return _redis_client