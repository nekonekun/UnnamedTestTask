"""Redis adapter."""
import logging

import redis

logger = logging.getLogger('digest.redis')


class RedisStorage:
    """Redis adapter."""

    def __init__(self, url: str):
        """Initialize Redis client.

        :param url: Redis Url
        :type url: str
        """
        self.client = redis.Redis.from_url(url, decode_responses=True)

    def store(self, user_id: int, data: str):
        """Store data to Redis.

        :param user_id: user ID to be used as key
        :type user_id: int
        :param data: data to store. Should be JSON, but no check is implemented
        :type data: str
        :return: None
        """
        self.client.set(user_id, data)
