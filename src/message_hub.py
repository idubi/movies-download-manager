from confluent_kafka import Producer, Consumer
import json


class MessageHub:
    def __init__(self, kafka_config):
        self.kafka_config = kafka_config
        self.producer = Producer(kafka_config)

    def send_message(self, topic, key, value):
        """
        Sends a message to the specified Kafka topic.
        """
        self.producer.produce(topic, key=key, value=json.dumps(value))
        self.producer.flush()
        print(f"Message sent to topic '{topic}': {value}")

    def consume_messages(self, topic, group_id, callback):
        """
        Consumes messages from the specified Kafka topic and processes them using the callback.
        """
        consumer_config = {
            **self.kafka_config,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        }
        consumer = Consumer(consumer_config)
        consumer.subscribe([topic])

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue

                # Process the message using the callback
                value = json.loads(msg.value().decode("utf-8"))
                callback(value)

        except KeyboardInterrupt:
            print("Stopping consumer...")
        finally:
            consumer.close()


# Example usage of the Message Hub
if __name__ == "__main__":
    kafka_config = {
        "bootstrap.servers": "localhost:9092",  # Replace with your Kafka server
    }

    message_hub = MessageHub(kafka_config)

    # Example: Sending a message
    task = {
        "link": "https://example.com/video1",
        "name": "movie1",
        "folder_name": "capsule1",
    }
    message_hub.send_message("download-requests", key=task["name"], value=task)

    # Example: Consuming messages
    def process_message(message):
        print(f"Processing message: {message}")

    message_hub.consume_messages(
        "download-status", group_id="status-consumer-group", callback=process_message
    )
