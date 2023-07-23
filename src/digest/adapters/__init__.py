"""Adapters collection."""
from digest.adapters.database import Gateway
from digest.adapters.rabbit import RabbitReader
from digest.adapters.storage import RedisStorage

__all__ = ('Gateway', 'RabbitReader', 'RedisStorage')
