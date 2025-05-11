#pyenv virtualenvs 
#pyenv virtualenv 3.12.7 browser-cookies
pyenv local download-manager




#List Kafka Topics: Use the following command to list all Kafka topics:
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
#Create a Kafka Topic: Create a topic
docker exec -it kafka kafka-topics --create --topic test --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1


#MONITOR : Consume Messages: Start a Kafka consumer to monitor messages in a topic:
docker exec -it kafka kafka-topics --describe --topic test --bootstrap-server localhost:9092

#Produce Messages: Start a Kafka producer to send messages to a topic:
docker exec -it kafka kafka-console-producer --bootstrap-server localhost:9092 --topic download-requests



# ffmped and yt-dlp installation
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp
chmod a+rx ~/.local/bin/yt-dlp  # Make executable


sudo apt update
sudo apt install ffmpeg

#start kafka and zookeeper
docker-compose up -d

# execute services
python src/config_manager.py
python src/download_manager.py



#  installing helm kafka : 
helm install my-release oci://registry-1.docker.io/bitnamicharts/kafka


