"""
kafka producer, push transition request status to kafka queue

IBM Corporation, 2017, jochen kappel
"""

import json
from flask import current_app as app
from kafka import KafkaProducer
from .ans_driver_config import ConfigReader

class Kafka:
    """
    implements the kafka client
    """
    def __init__(self, logger):
        """
        initialize, get configurat
        """
        self.logger = logger
        self.kproducer = None
        self.logger.info('reading kafka config')
        self.config = ConfigReader()
        self.kafkaUrl = self.config.getDriverProperties('responseKafkaConnectionUrl')
        self.kafkaTopic = self.config.getDriverProperties('responseKafkaTopicName')
        self.logger.debug('Trying to setup kafka producer on: '+self.kafkaUrl+', topic: '+ self.kafkaTopic)

        try:
            self.kproducer = KafkaProducer(bootstrap_servers=self.kafkaUrl,value_serializer=lambda m: json.dumps(m).encode('ascii'),api_version=(0,10) )
        except Exception as e:
            self.logger.error('could not connect to kafka server at '+self.kafkaUrl+' no messages will be published')
            self.producer = None


    def sendLifecycleEvent(self, msg):
        self.logger.debug('sending message to kafka '+str(msg))

		# if have a valid producer then send a kafka message, otherwise do nothin
        if self.kproducer != None:
            self.logger.debug('have valid producer')
            self.logger.debug("sending transition event to Kafka topic "+self.kafkaTopic)

            future = self.kproducer.send(self.kafkaTopic, dict(msg))

            try:
                record_metadata = future.get(timeout=10)
                self.logger.debug('msg metadata: '+str(record_metadata))
            except KafkaError:
                #log.exception()
                pass
        else:
            self.logger.debug('no valid kafka producer found')
