import os
import sys
from pathlib import Path

from alembic.config import CommandLine, Config

PROJECT_PATH = Path(__file__).parent.parent.resolve()


def main():
    """Alembic entrypoint"""
    alembic = CommandLine()
    alembic.parser.add_argument(
        '--postgres-username',
        help='Postgres username',
        metavar='user',
        default=os.environ.get('POSTGRES_USER'),
    )
    alembic.parser.add_argument(
        '--postgres-password',
        help='Postgres password',
        metavar='pass',
        default=os.environ.get('POSTGRES_PASSWORD'),
    )
    alembic.parser.add_argument(
        '--postgres-host',
        help='Postgres host',
        metavar='host',
        default=os.environ.get('DIGEST_POSTGRES_HOST', 'localhost'),
    )
    alembic.parser.add_argument(
        '--postgres-port',
        help='Postgres port',
        metavar='5432',
        default=os.environ.get('DIGEST_POSTGRES_PORT', 5432),
    )
    alembic.parser.add_argument(
        '--postgres-database',
        help='Postgres database',
        metavar='db',
        default=os.environ.get('POSTGRES_DB'),
    )
    options = alembic.parser.parse_args()
    username = options.postgres_username
    password = options.postgres_password
    host = options.postgres_host
    port = options.postgres_port
    db = options.postgres_database
    options.database = (
        f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db}'
    )

    if not os.path.isabs(options.config):
        options.config = os.path.join(PROJECT_PATH, options.config)

    config = Config(
        file_=options.config, ini_section=options.name, cmd_opts=options
    )

    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option(
            'script_location', os.path.join(PROJECT_PATH, alembic_location)
        )

    config.set_main_option('sqlalchemy.url', options.database)

    sys.exit(alembic.run_cmd(config, options))
