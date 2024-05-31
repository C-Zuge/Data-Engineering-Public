## Kafka Project
This file means to cover basic aspects of kafka deploy and basic commands.

### Create a topic
```bash
# Structure
docker-compose exec <container_name> kafka-topics --create --topic <topic_name> --partitions <n_part> --replication-factor <rep_fac> --if-not-exists  --bootstrap-server <ip>:<port>

# Example
docker-compose exec kafka1 kafka-topics --create --topic kafka-topic-init --partitions 1 --replication-factor 1 --if-not-exists  --bootstrap-server localhost:9092
```

### Confirm topic creation
```bash
#Structure
docker-compose exec <container_name> kafka-topics --describe --topic <topic_name> --bootstrap-server <ip>:<port>

#Example
docker-compose exec kafka1 kafka-topics --describe --topic kafka-topic-init  --bootstrap-server localhost:9092
```

### Produce some messages to topic from terminal
```bash
docker-compose exec kafka1  bash -c "seq 100 | kafka-console-producer --request-required-acks 1 --broker-list <ip>:<port> --topic <topic_name> && echo 'Produced 100 messages.'"

docker-compose exec kafka1  bash -c "seq 100 | kafka-console-producer --request-required-acks 1 --broker-list localhost:9092 --topic kafka-topic-init && echo 'Produced 100 messages.'"
```

### Consume topic's info from terminal
```bash
docker-compose exec <container_name>  kafka-console-consumer --bootstrap-server <ip>:<port> --topic <topic_name> --from-beginning --max-messages <n_max>

docker-compose exec kafka1  kafka-console-consumer --bootstrap-server localhost:9092 --topic kafka-topic-init --from-beginning --max-messages 100
```