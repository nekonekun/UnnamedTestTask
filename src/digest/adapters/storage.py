"""Redis adapter."""
import logging

import redis

logger = logging.getLogger('digest.redis')


class RedisStorage:
    """Redis adapter."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """Initialize Redis client.

        :param host: hostname
        :type host: str
        :param port: port
        :type port: int
        :param db: database number
        :type db: int
        """
        self.client = redis.Redis(
            host=host, port=port, db=db, decode_responses=True
        )

    def store(self, user_id: int, data: str):
        """Store data to Redis.

        :param user_id: user ID to be used as key
        :type user_id: int
        :param data: data to store. Should be JSON, but no check is implemented
        :type data: str
        :return: None
        """
        self.client.set(user_id, data)
