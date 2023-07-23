def test_redis_store_and_update(redis_client):
    redis_client.client.delete('1')
    assert redis_client.client.get('1') is None
    redis_client.store('1', 'data')
    assert redis_client.client.get('1') == 'data'
    redis_client.store('1', 'new data')
    assert redis_client.client.get('1') == 'new data'
