import logging

import redis

logger = logging.getLogger('digest.redis')


class RedisStorage:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host, port=port, db=db, decode_responses=True
        )

    def store(self, user_id: int, data: str):
        self.client.set(user_id, data)
