import pika
import os
from dotenv import load_dotenv


load_dotenv()

class MessageBroker:
    def __init__(self) -> None:
        self.connection = pika.BlockingConnection(pika.URLParameters(os.getenv('RABBITMQ_URL')))
        self.channel = self.connection.channel()

    def publish(self, queue_name: str, message: str) -> None:
        self.channel.queue_declare(queue=queue_name, durable=False)
        self.channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        print(f"Sent: {message}")

    def consume(self, queue_name: str, callback) -> None:
        self.channel.queue_declare(queue=queue_name, durable=False)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(f"Waiting for messages in {queue_name}. To exit press CTRL+C")
        self.channel.start_consuming()

    def consume_one(self, queue, callback):
        self.channel.queue_declare(queue=queue, durable=False)

        def stop_consuming_callback(ch, method, properties, body):
            callback(ch, method, properties, body)
            self.channel.stop_consuming()

        self.channel.basic_consume(queue=queue, on_message_callback=stop_consuming_callback, auto_ack=True)
        print(f"Waiting for a single message in {queue}.")
        self.channel.start_consuming()

    def close(self) -> None:
        self.channel.close()
        self.connection.close()

