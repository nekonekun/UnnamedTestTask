import pytest
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from digest.adapters.database import Gateway
from digest.adapters.storage import RedisStorage
from digest.adapters.rabbit import RabbitReader
from digest.services.digester import Digester
from digest.services.filters import dummy_filter


@pytest.fixture(scope='session')
def sessionmaker_():
    username = os.environ.get('POSTGRES_USER')
    password = os.environ.get('POSTGRES_PASSWORD')
    host = os.environ.get('DIGEST_POSTGRES_HOST', 'localhost')
    port = os.environ.get('DIGEST_POSTGRES_PORT', 5432)
    db = os.environ.get('POSTGRES_DB')
    postgres_url = (
        f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db}'
    )
    engine = create_engine(postgres_url)
    return sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
def refill_database(sessionmaker_):
    with sessionmaker_() as s:
        stmt = text("""delete from users_subscriptions; delete from posts_digests; delete from digests; delete from posts; delete from subscriptions; delete from users;""")
        s.execute(stmt)
        stmt = text("""alter sequence digests_id_seq restart with 1; alter sequence posts_id_seq restart with 1; alter sequence subscriptions_id_seq restart with 1; alter sequence users_id_seq restart with 1;""")
        s.execute(stmt)
        stmt = text("""insert into users (name) values ('Football Fan'), ('News Reader'), ('Denier');""")
        s.execute(stmt)
        stmt = text("""insert into subscriptions (source) values ('Football news'), ('Russian news'), ('World news'), ('Paraguay news'), ('Crypto news');""")
        s.execute(stmt)
        stmt = text("""insert into posts (subscription_id, content, popularity) values (1, 'Товарищеские матчи. «МЮ» против «Арсенала», «Челси» играет с «Брайтоном», игра «Барсы» и «Юве» отменена', 1), (1, 'Мбаппе интересен «Тоттенхэму», «МЮ» и «Челси». Крупнейшее предложение сделает «Аль-Хилаль», но «ПСЖ» знает, что Килиан к саудовцам не поедет', 2), (1, ' Хусаинов об удалении у «Пари НН»: «Александров помешал возникновению момента – прямая красная. Для такого решения нужны яйца»', 3), (1, '«Рома» не взяла Шомуродова в турне по Португалии. Форвард не входит в планы Моуринью', 4), (1, 'Глава «Локо» о видео Дзюбы с торчащим игрушечным бананом: «Я не видел. Если вы это смотрели, значит, вам интересно»', 5), (1, 'Джузеппе Росси завершил карьеру. Экс-форварду «МЮ», «Вильярреала» и сборной Италии 36 лет', 6), (1, 'Гендиректор «Рубина»: «Задача – вернуться в топ России. О борьбе только за сохранение места речи нет»', 7), (1, 'Орлов об удалении у «Пари НН»: «Бакаев выходил один на один, фол тянул на красную. Все по закону»', 8), (1, 'Глава «Локо» о Fan ID: «Продали около тысячи абонементов на сезон. У всех московских клубов меньше 10 000. Не та ситуация, которой мы могли бы гордиться»', 9), (1, 'Гильермо Абаскаль: «Уважаем философию «Спартака» – хотим доминировать, атаковать. Если против тебя стоят стеной, нужно знать, как это преодолеть»', 10);""")
        s.execute(stmt)
        stmt = text("""insert into posts (subscription_id, content, popularity) values (2, 'Россиянам объяснили правила начисления отпускных', 5), (2, 'В полях под Тулой нашли ловушки из заточенной арматуры', 6), (2, 'В российском регионе зарегистрировали случаи лихорадки Западного Нила', 5), (2, 'В Бородино прошел финал игры «Зарница 2.0»', 4), (2, 'Минтранс анонсировал новые меры регулирования движения электросамокатов', 5);""")
        s.execute(stmt)
        stmt = text("""insert into posts (subscription_id, content, popularity) values (3, 'В Турции произошло землетрясение', 4), (3, 'Синоптики спрогнозировали переход аномальной жары из Европы в Турци', 5), (3, 'Тещу президента Южной Кореи задержали за подделку документа', 6), (3, 'Трамп пожаловался на невиданное ранее давление на своих юристов', 5), (3, 'Гонконг ограничил движение общественного транспорта и занятия в школах', 3);""")
        s.execute(stmt)
        stmt = text("""insert into posts (subscription_id, content, popularity) values (4, 'Глава Парагвая отметил столетие ВВС прыжком с парашютом', 1), (4, 'США не смогли повлиять на выборы в Парагвае, считает посол Писарев', 1)""")
        s.execute(stmt)
        stmt = text("""insert into posts (subscription_id, content, popularity) values (5, 'МВД и «Стопнаркотик» договорились выявлять незаконные крипто-транзакции', 8), (5, 'Рынку криптовалют предсказали ужасный сценарий', 7), (5, 'Обнаружена новая опасность криптовалюты', 8)""")
        s.execute(stmt)
        stmt = text("""insert into users_subscriptions (user_id, subscription_id) values (1, 1), (2, 2), (2, 3), (2, 4);""")
        s.execute(stmt)
        s.commit()


@pytest.fixture
def gateway(sessionmaker_):
    return Gateway(sessionmaker_)


@pytest.fixture
def redis_client():
    host = os.environ.get('DIGEST_REDIS_HOST', 'localhost')
    port = os.environ.get('DIGEST_REDIS_PORT', 6379)
    db = os.environ.get('DIGEST_REDIS_DB', '0')
    storage = RedisStorage(host, port, db)
    storage.client.delete(1, 2, 3)
    return RedisStorage(host, port, db)


@pytest.fixture
def rabbit_reader():
    host = os.environ.get('DIGEST_RABBIT_HOST', 'localhost')
    port = os.environ.get('DIGEST_RABBIT_PORT', 5672)
    username = os.environ.get('DIGEST_RABBIT_USERNAME')
    password = os.environ.get('DIGEST_RABBIT_PASSWORD')
    queue = os.environ.get('DIGEST_RABBIT_QUEUE')
    return RabbitReader(queue, host, port, username, password)


class FakeRabbitReader(RabbitReader):
    def __init__(self):
        self.user_list = [1, 2, 3]

    def message_generator(self, limit: int = 3):
        yield from self.user_list


@pytest.fixture
def fake_rabbit_reader():
    return FakeRabbitReader()


@pytest.fixture
def digester(gateway, redis_client, fake_rabbit_reader):
    return Digester(
        gateway,
        fake_rabbit_reader,
        redis_client,
        dummy_filter,
    )
