"""Digester module."""
import logging
from collections.abc import Callable
from datetime import datetime

from digest.adapters.database import Gateway
from digest.adapters.rabbit import RabbitReader
from digest.adapters.storage import RedisStorage
from digest.schemas import DigestDTO

logger = logging.getLogger('digest.digester')


class Digester:
    """Digester.

    Reads user IDs from RabbitMQ.
    Then compose digest for each user ID.
    Then saves them to Postgres and to Redis.
    """

    def __init__(
        self,
        gateway: Gateway,
        rabbit_reader: RabbitReader,
        redis_storage: RedisStorage,
        filter_function: Callable[..., list[int]],
    ):
        """Initialize Digester.

        User subscriptions and Posts will be read from gateway.
        User IDs will be read from rabbit_reader.
        Posts will be filtered with compose_function.
        Composed Digests will be stored to redis_storage.

        :param gateway: database adapter.
        :type gateway: Gateway
        :param rabbit_reader: RabbitMQ listener.
        :type rabbit_reader: RabbitReader
        :param redis_storage: Redis storage.
        :type redis_storage: RedisStorage
        :param filter_function: filter function
        :type filter_function: Callable
        """
        self.gateway = gateway
        self.rabbit_reader = rabbit_reader
        self.redis_storage = redis_storage
        self.filter_function = filter_function

    def make_digest(self, user_id: int, limit: int = 5) -> DigestDTO:
        """Make Digest for given user and store it to PostgresQL.

        :param user_id: target user ID
        :type user_id: int
        :param limit: number of posts to be used
        :type limit: int
        :return: composed digest
        """
        posts = self.gateway.read_posts_for_user(user_id)
        post_ids = self.filter_function(*posts, limit=limit)
        return self.gateway.create_digest(user_id, *post_ids)

    def store_digest(self, digest_data: DigestDTO):
        """Store digest to Redis.

        :param digest_data: digest to be stored
        :type digest_data: DigestDTO
        :return: None
        """
        self.redis_storage.store(
            digest_data.user_id, digest_data.model_dump_json()
        )

    def flow(self, user_id: int):
        """Compose digest for given user and store it to Redis.

        :param user_id: target user ID
        :type user_id: int
        :return: None
        """
        digest_data = self.make_digest(user_id)
        if digest_data:
            self.store_digest(digest_data)
        else:
            self.store_digest(
                DigestDTO(
                    id=0,
                    user_id=user_id,
                    timestamp=datetime.now().isoformat(),
                    posts=[],
                )
            )

    def __call__(self):
        """Start the whole process.

        Listen to RabbitMQ, and apply flow to every user ID.
        """
        logger.error('Start listening')
        for user_id in self.rabbit_reader.message_generator():
            self.flow(user_id)
