import pika


class RabbitReader:
    def __init__(
        self,
        queue: str,
        host: str = 'localhost',
        port: int = 5672,
        username: str | None = None,
        password: str | None = None,
    ):
        if username and password:
            credentials = pika.credentials.PlainCredentials(username, password)
            self.connection_parameters = pika.ConnectionParameters(
                host=host, port=port, credentials=credentials
            )
        else:
            self.connection_parameters = pika.ConnectionParameters(
                host=host, port=port
            )
        self.queue = queue

    def message_generator(self):
        connection = pika.BlockingConnection(self.connection_parameters)
        channel = connection.channel()

        channel.queue_declare(queue=self.queue)
        try:
            for method, _properties, body in channel.consume(self.queue):
                channel.basic_ack(method.delivery_tag)
                yield body.decode()
        except KeyboardInterrupt:
            connection.close()
            return
