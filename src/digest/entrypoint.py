"""Main entrypoint module."""
import logging
import os
from argparse import ArgumentParser
from collections import defaultdict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from digest.adapters import Gateway, RabbitReader, RedisStorage
from digest.services.digester import Digester
from digest.services.filters import at_least_one_subscription

LEVELS = defaultdict(lambda: 'WARN', {1: 'INFO', 2: 'DEBUG'})

logger = logging.getLogger('digest')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

parser = ArgumentParser()

group = parser.add_argument_group('PostgresQL')
group.add_argument(
    '--postgres-username',
    help='Postgres username',
    metavar='user',
    default=os.environ.get('POSTGRES_USER'),
)
group.add_argument(
    '--postgres-password',
    help='Postgres password',
    metavar='pass',
    default=os.environ.get('POSTGRES_PASSWORD'),
)
group.add_argument(
    '--postgres-host',
    help='Postgres host',
    metavar='host',
    default=os.environ.get('DIGEST_POSTGRES_HOST', 'localhost'),
)
group.add_argument(
    '--postgres-port',
    help='Postgres port',
    metavar='5432',
    default=os.environ.get('DIGEST_POSTGRES_PORT', 5432),
)
group.add_argument(
    '--postgres-database',
    help='Postgres database',
    metavar='db',
    default=os.environ.get('POSTGRES_DB'),
)

group = parser.add_argument_group('RabbitMQ')
group.add_argument(
    '--rabbit-host',
    help='RabbitMQ host',
    metavar='host',
    default=os.environ.get('DIGEST_RABBIT_HOST', 'localhost'),
)
group.add_argument(
    '--rabbit-port',
    help='RabbitMQ port',
    metavar='5672',
    default=os.environ.get('DIGEST_RABBIT_PORT', 5672),
)
group.add_argument(
    '--rabbit-username',
    help='RabbitMQ username',
    metavar='user',
    default=os.environ.get('DIGEST_RABBIT_USERNAME'),
)
group.add_argument(
    '--rabbit-password',
    help='RabbitMQ password',
    metavar='pass',
    default=os.environ.get('DIGEST_RABBIT_PASSWORD'),
)
group.add_argument(
    '--rabbit-queue',
    help='RabbitMQ queue name',
    metavar='queue',
    default=os.environ.get('DIGEST_RABBIT_QUEUE'),
)

group = parser.add_argument_group('Redis')
group.add_argument(
    '--redis-host',
    help='Redis host',
    metavar='HOST',
    default=os.environ.get('DIGEST_REDIS_HOST'),
)
group.add_argument(
    '--redis-port',
    help='Redis port',
    metavar='6379',
    default=os.environ.get('DIGEST_REDIS_PORT', '6379'),
)
group.add_argument(
    '--redis-db',
    help='Redis db number',
    metavar='0',
    default=os.environ.get('DIGEST_REDIS_DB', '0'),
)

group = parser.add_argument_group('Misc')
parser.add_argument('--verbose', '-v', action='count', default=0)


def main():
    """Parse arguments, initialize Digester and start flow."""
    args = parser.parse_args()

    logger.setLevel(LEVELS[args.verbose])

    logger.info('Setting up database adapter')
    username = args.postgres_username
    password = args.postgres_password
    host = args.postgres_host
    port = args.postgres_port
    db = args.postgres_database
    postgres_url = (
        f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db}'
    )
    engine = create_engine(postgres_url)
    sessionmaker_ = sessionmaker(engine)
    gateway = Gateway(sessionmaker_)
    logger.info('Database adapter has been set')

    logger.info('Setting up RabbitMQ adapter')
    host = args.rabbit_host
    port = args.rabbit_port
    username = args.rabbit_username
    password = args.rabbit_password
    queue = args.rabbit_queue
    rabbit_reader = RabbitReader(queue, host, port, username, password)
    logger.info('RabbitMQ adapter has been set')

    logger.info('Setting up Redis adapter')
    host = args.redis_host
    port = args.redis_port
    db = args.redis_db
    redis_storage = RedisStorage(host, port, db)
    logger.info('Redis adapter has been set')

    compose_function = at_least_one_subscription

    digester = Digester(
        gateway, rabbit_reader, redis_storage, compose_function
    )

    logger.info('Starting main method')
    digester()
