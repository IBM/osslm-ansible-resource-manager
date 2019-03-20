"""
kafka producer, push transition request status to kafka queue

IBM Corporation, 2017, jochen kappel
"""

from kafka.client_async import KafkaClient
from kafka.protocol import admin
from kafka.protocol.api import Response, Request
from kafka.protocol import types
from flask import current_app as app


def ensure_topic( topic, num_partitions, replication_factor,
                  logger, timeout_ms=3000, brokers='localhost' ):
    logger.debug('checking kafka for topic '+topic)
    client = KafkaClient(bootstrap_servers=brokers)

    if topic not in client.cluster.topics(exclude_internal_topics=True):
        logger.debug('creating kafka topic '+topic)

        request = admin.CreateTopicsRequest_v0(
            create_topic_requests=[(
                topic,
                num_partitions,
                replication_factor,
                [],  # Partition assignment
                [],  # Configs
            )],
            timeout=timeout_ms
        )
        future = client.send(client.least_loaded_node(), request)
        client.poll(timeout_ms=timeout_ms, future=future)
        result = future.value
        error_code = result.topic_errors[0][1]
        # 0: success
        # 36: already exists, check topic
        if error_code == 0:
            logger.debug('kafka topic '+topic+' created')
            return
        elif error_code != 36:
            logger.error('error creating kafka topic '+topic)
            raise Exception('Unknown error code during creation of topic `{}`: {}'.format(
                topic, error_code))

    else:
        logger.debug('kafka topic '+topic+' exists')
#ensure_topic( topic='alm_test',num_partitions=1, brokers='kafka:9092')
