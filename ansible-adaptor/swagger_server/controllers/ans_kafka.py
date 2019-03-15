"""
kafka producer, push transition request status to kafka queue

IBM Corporation, 2017, jochen kappel
"""

import json
from flask import current_app as app
from kafka import KafkaProducer
from kafka.errors import KafkaError
from .ans_driver_config import ConfigReader
from .ans_kafka_topic import *


class Kafka:
    """
    implements the kafka client
    """
    def __init__(self, logger):
        """
        initialize, get configuration
        """
        self.logger = logger
        self.kproducer = None
        self.logger.debug('reading kafka config')
        self.config = ConfigReader()
        self.kafkaUrl = self.config.getDriverProperties('responseKafkaConnectionUrl')
        self.kafkaTopic = self.config.getDriverProperties('responseKafkaTopicName')

        try:
            self.kproducer = KafkaProducer(bootstrap_servers=self.kafkaUrl, value_serializer=lambda m: json.dumps(m).encode('ascii'), api_version=(0, 10))
            self.logger.debug('kafka producer is up')
        except Exception as e:
            self.logger.error('could not connect to kafka server at ' + self.kafkaUrl+' no messages will be published')
            self.producer = None

        try:
            ensure_topic( topic=self.kafkaTopic, num_partitions=1, brokers=self.kafkaUrl,
                           logger=self.logger )
        except Exception as e:
            self.logger.error('could not create kafka topic at ' + self.kafkaUrl)
            self.producer = None

    def sendLifecycleEvent(self, msg):
        self.logger.debug('message is valid json '+ str(json.dumps(msg)))

        # if have a valid producer then send a kafka message, otherwise do nothin
        if self.kproducer is not None:
            self.logger.debug('have valid producer')
            self.logger.debug("sending transition event to Kafka topic "+self.kafkaTopic)

            future = self.kproducer.send(self.kafkaTopic, dict(msg))

            try:
                record_metadata = future.get(timeout=10)
                self.logger.debug('msg metadata: '+str(record_metadata))
            except KafkaError as err:
                self.logger.error(str(err))

        else:
            self.logger.debug('no valid kafka producer found')
