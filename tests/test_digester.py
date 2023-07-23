import json
from digest.schemas import DigestDTO


def test_make_digest(digester):
    digest_ = digester.make_digest(1, 5)
    assert digest_.user_id == 1
    assert len(digest_.posts) == 5


def test_store_digest(digester):
    digest_ = digester.make_digest(1, 5)
    digester.store_digest(digest_)
    digest_ = DigestDTO.model_validate(json.loads(digester.redis_storage.client.get(1)))
    assert digest_.user_id == 1
    assert len(digest_.posts) == 5


def test_flow(digester):
    digester.flow(2)
    digest_ = DigestDTO.model_validate(json.loads(digester.redis_storage.client.get(2)))
    assert digest_.user_id == 2
    assert len(digest_.posts) == 5


def test_run(digester):
    digester()
    digest_ = DigestDTO.model_validate(json.loads(digester.redis_storage.client.get(1)))
    assert digest_.user_id == 1
    assert len(digest_.posts) == 5
    digest_ = DigestDTO.model_validate(json.loads(digester.redis_storage.client.get(2)))
    assert digest_.user_id == 2
    assert len(digest_.posts) == 5
    digest_ = DigestDTO.model_validate(json.loads(digester.redis_storage.client.get(3)))
    assert digest_.user_id == 3
    assert len(digest_.posts) == 0

