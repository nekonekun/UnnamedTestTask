"""Main entrypoint module."""
import logging

from pydantic import (
    Field,
    FieldValidationInfo,
    PostgresDsn,
    RedisDsn,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from digest.adapters import Gateway, RabbitReader, RedisStorage
from digest.services.digester import Digester
from digest.services.filters import at_least_one_subscription

logger = logging.getLogger('digest')


class Settings(BaseSettings):
    """Script settings class."""

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    postgres_user: str
    postgres_password: str
    postgres_db: str

    postgres_db_engine: str = Field(
        'postgresql+psycopg2', alias='digest_db_engine'
    )
    postgres_host: str = Field('localhost', alias='digest_postgres_host')
    postgres_port: int = Field(5432, alias='digest_postgres_port')

    database_url: PostgresDsn | None = None

    rabbit_host: str = Field('localhost', alias='digest_rabbit_host')
    rabbit_port: int = Field(5672, alias='digest_rabbit_port')
    rabbit_username: str | None = Field(None, alias='digest_rabbit_username')
    rabbit_password: str | None = Field(None, alias='digest_rabbit_password')
    rabbit_queue: str = Field(..., alias='digest_rabbit_queue')

    redis_host: str = Field('localhost', alias='digest_redis_host')
    redis_port: int = Field(6379, alias='digest_redis_port')
    redis_db: int = Field(0, alias='digest_redis_db')

    redis_url: RedisDsn | None = None

    verbosity: int = Field(0, alias='digest_verbosity', ge=0)

    severity_name: str | None = None

    @field_validator('database_url')
    def assemble_db_dsn(cls, value: str, info: FieldValidationInfo):  # noqa
        """Assemble database url if not provided."""
        if isinstance(value, str):
            return value
        context = info.data
        return str(
            PostgresDsn.build(
                scheme=context.get('postgres_db_engine'),
                username=context.get('postgres_user'),
                password=context.get('postgres_password'),
                host=context.get('postgres_host'),
                port=context.get('postgres_port'),
                path=context.get('postgres_db') or '',
            )
        )

    @field_validator('redis_url')
    def assemble_redis_dsn(cls, value: str, info: FieldValidationInfo):  # noqa
        """Assemble redis URL if not provided."""
        if isinstance(value, str):
            return value
        context = info.data
        return str(
            RedisDsn.build(
                scheme='redis',
                host=context.get('redis_host'),
                port=context.get('redis_port'),
                path=str(context.get('redis_db')),
            )
        )

    @field_validator('severity_name')
    def compute_severity_name(
        cls, value: str, info: FieldValidationInfo  # noqa
    ):
        """Compute logger severity based on verbosity level."""
        context = info.data
        if context.get('verbosity') == 0:
            return 'ERROR'
        if context.get('verbosity') == 1:
            return 'WARN'
        if context.get('verbosity') == 2:
            return 'INFO'
        return 'DEBUG'


def main():
    """Parse arguments, initialize Digester and start flow."""
    settings = Settings()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(settings.severity_name)

    logger.info('Setting up database adapter')
    engine = create_engine(settings.database_url)
    sessionmaker_ = sessionmaker(engine)
    gateway = Gateway(sessionmaker_)
    logger.info('Database adapter has been set')

    logger.info('Setting up RabbitMQ adapter')
    host = settings.rabbit_host
    port = settings.rabbit_port
    username = settings.rabbit_username
    password = settings.rabbit_password
    queue = settings.rabbit_queue
    rabbit_reader = RabbitReader(queue, host, port, username, password)
    logger.info('RabbitMQ adapter has been set')

    logger.info('Setting up Redis adapter')
    redis_storage = RedisStorage(settings.redis_url)
    logger.info('Redis adapter has been set')

    compose_function = at_least_one_subscription

    digester = Digester(
        gateway, rabbit_reader, redis_storage, compose_function
    )

    logger.info('Starting main method')
    digester()
