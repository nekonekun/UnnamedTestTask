import logging
from collections.abc import Callable
from datetime import datetime

from digest.adapters.database import Gateway
from digest.adapters.rabbit import RabbitReader
from digest.adapters.storage import RedisStorage
from digest.schemas import DigestDTO

logger = logging.getLogger('digest.digester')


class Digester:
    def __init__(
        self,
        gateway: Gateway,
        rabbit_reader: RabbitReader,
        redis_storage: RedisStorage,
        compose_function: Callable[..., list[int]],
    ):
        self.gateway = gateway
        self.rabbit_reader = rabbit_reader
        self.redis_storage = redis_storage
        self.compose_function = compose_function

    def make_digest(self, user_id: int, limit: int = 5) -> DigestDTO:
        """Filter posts and compose digest"""
        posts = self.gateway.read_posts_for_user(user_id)
        post_ids = self.compose_function(*posts, limit=limit)
        return self.gateway.create_digest(user_id, *post_ids)

    def store_digest(self, digest_data: DigestDTO):
        """Return digest to main app"""
        self.redis_storage.store(
            digest_data.user_id, digest_data.model_dump_json()
        )

    def flow(self, user_id: int):
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
        """Start digester process"""
        logger.error('Start listening')
        for user_id in self.rabbit_reader.message_generator():
            self.flow(user_id)
