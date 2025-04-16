from confluent_kafka import Producer, Consumer, KafkaError
import asyncio
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


    async def consume_messages_async(self, topic, group_id):
        """
        Asynchronous message consumer that yields messages one at a time
        """
        consumer = Consumer({
            **self.kafka_config,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe([topic])

        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                
                # Convert message value from bytes to dict if needed
                try:
                    value = self._decode_message(msg.value())
                    yield value
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    continue

                # Give control back to event loop periodically
                await asyncio.sleep(0)
        finally:
            consumer.close()

    def _decode_message(self, message_value):
        """
        Helper method to decode message value from bytes to dict
        """
        if isinstance(message_value, bytes):
            return json.loads(message_value.decode('utf-8'))
        return message_value


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
