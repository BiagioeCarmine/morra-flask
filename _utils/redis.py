from os import getenv

import redis

redis_host = getenv("REDIS_HOST")

redis_db = redis.Redis(host=redis_host)
