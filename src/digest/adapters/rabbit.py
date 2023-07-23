"""RabbitMQ adapter."""
import pika


class RabbitReader:
    """RabbitMQ adapter."""

    def __init__(
        self,
        queue: str,
        host: str = 'localhost',
        port: int = 5672,
        username: str | None = None,
        password: str | None = None,
    ):
        """Prepare adapter settings.

        Connection WILL NOT be initialized here.

        :param queue: queue name
        :type queue: str
        :param host: hostname
        :type host: str
        :param port: port
        :type port: int
        :param username: username
        :type username: str
        :param password: password
        :type password: str
        """
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
        """Start listening process.

        Yields received messages one-by-one.

        :return: user ID as string
        """
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
