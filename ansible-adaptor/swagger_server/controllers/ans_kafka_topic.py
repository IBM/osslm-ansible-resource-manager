"""
kafka producer, push transition request status to kafka queue

IBM Corporation, 2017, jochen kappel
"""

from kafka.client_async import KafkaClient
from kafka.protocol import admin
from kafka.protocol.api import Response, Request
from kafka.protocol import types
from flask import current_app as app
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


def ensure_topic( topic, num_partitions, replication_factor, logger,
                  timeout_ms=3000, brokers='localhost' ):

    adminclient = KafkaAdminClient(bootstrap_servers=brokers, client_id='ansible-rm')

    topic_list = []
    topic_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))

    try:
        adminclient.create_topics(new_topics=topic_list, validate_only=False)
        # adminclient.delete_topics(topic_list)
        logger.info('kafka topic '+topic+' created')
    except TopicAlreadyExistsError as e:
        logger.info('kafka topic '+topic+' exists')
    except Exception as e:
        logger.error('error creating kafka topic '+topic)
        raise Exception('Unknown error code during creation of topic `{}`: {}'.format(
                        topic, str(e)))
