from kafka import KafkaConsumer
import json
import time


class ConsumerServer(KafkaConsumer):

    default_broker_configs = {
        'bootstrap_servers' : 'localhost:9092',
        'auto_offset_reset' : 'earliest',
        'enable_auto_commit' : True,
        'value_deserializer' : lambda x: json.loads(x.decode('utf-8')),
        'group_id' : 'udacity_project_2_kafka_consumer',
    }
    
    def __init__(self, topic, broker_configs = default_broker_configs):
        self.topic = topic
        super().__init__(self.topic, **broker_configs)
        

    def consume_data(self):
        for data in self:
            print(data)
        
if __name__ == '__main__':
    topic = 'udacity.project2.police.calls'
    consumer = ConsumerServer(topic)
    consumer.consume_data()