from kafka import KafkaProducer
import json
import time


class ProducerServer(KafkaProducer):

    def __init__(self, input_file, topic, **kwargs):
        super().__init__(**kwargs)
        self.input_file = input_file
        self.topic = topic

    def generate_data(self):
        with open(self.input_file) as f:
            f = json.load(f)
            for item in f:
                message = self.dict_to_binary(item)
                self.send(self.topic, value=message).get()
                time.sleep(1)

    def dict_to_binary(self, json_dict):
        return json.dumps(json_dict).encode('utf-8')
        