import redis
from os import getenv

redis_host = getenv("REDIS_HOST")

redis_db = redis.Redis(host=redis_host)
