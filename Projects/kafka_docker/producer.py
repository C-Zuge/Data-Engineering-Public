# from kafka import KafkaProducer
# import json
# import random
# from time import sleep
# from datetime import datetime

# # Create an instance of the Kafka producer
# producer = KafkaProducer(bootstrap_servers='localhost:9092',
#                             value_serializer=lambda v: str(v).encode('utf-8'))

# # Call the producer.send method with a producer-record
# print("Ctrl+c to Stop")
# while True:
#     producer.send('kafka-python-topic', random.randint(1,999))


from confluent_kafka import Producer
import socket
import random

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))



conf = {'bootstrap.servers': 'localhost:9092',
        'client.id': socket.gethostname()}

producer = Producer(conf)
while True:
    producer.produce(topic='kafka-topic-init', key="key", value=random.randint(1,999).to_bytes(2, 'big'),callback=acked)
    
    producer.poll(1) # Wait up to 1 second for events. Callbacks will be invoked during this method call if the message is acknowledged.
    # producer.flush() # For syncronous writes, use flush() method. This is typically a bad idea since it effectively limits throughput to the broker round trip time
