#start kafka
docker-compose up -d
#List Kafka Topics: Use the following command to list all Kafka topics:
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
#Create a Kafka Topic: Create a topic
docker exec -it kafka kafka-topics --create --topic test --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1


#MONITOR : Consume Messages: Start a Kafka consumer to monitor messages in a topic:
docker exec -it kafka kafka-topics --describe --topic test --bootstrap-server localhost:9092

#Produce Messages: Start a Kafka producer to send messages to a topic:
docker exec -it kafka kafka-console-producer --bootstrap-server localhost:9092 --topic download-requests
