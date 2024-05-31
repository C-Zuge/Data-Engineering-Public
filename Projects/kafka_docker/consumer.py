# import json 
# from kafka import KafkaConsumer

# consumer = KafkaConsumer(
#         'kafka-topic-init',
#         bootstrap_servers='localhost:9092',
#         max_poll_records = 100,
#         value_deserializer=lambda m: json.loads(m.decode('ascii')),
#         auto_offset_reset='earliest'#,'smallest'
#     )
# for msg in consumer:
#     print(msg)
#     print(json.loads(msg.value))

from confluent_kafka import Consumer, KafkaError, KafkaException
import sys

conf = {'bootstrap.servers': 'localhost:9092',
        'group.id': 'Consumer_tst',
        'auto.offset.reset': 'smallest'}

consumer = Consumer(conf)

running = True
MIN_COMMIT_COUNT = 1

def basic_consume_loop(consumer, topics):
    msg_count = 0
    try:
        consumer.subscribe(topics)

        while running:
            if msg_count > 100: shutdown()
            
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                msg_process(msg)
                msg_count += 1
                if msg_count % MIN_COMMIT_COUNT == 0:
                    consumer.commit(asynchronous=False)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def msg_process(Message):
    print(f"{Message =}")

def shutdown():
    running = False

basic_consume_loop(consumer,['kafka-topic-init'])