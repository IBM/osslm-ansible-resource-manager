#!/usr/bin/env python3
"""
ansible resource manager for ALM v1.1

IBM Corporation, 2017, jochen kappel
"""

import os
import logging
import logging.handlers
from distutils.dir_util import copy_tree
from os.path import dirname, abspath
import connexion
from .encoder import JSONEncoder
from .controllers.ans_driver_config import ConfigReader
from .controllers.ans_kafka import Kafka
from .controllers.ans_logging import LogstashFormatter
import uuid
import sys
import ssl

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = JSONEncoder

    log_level = os.environ.get('LOG_LEVEL')
    if log_level is None:
        log_level = 'INFO'

    log_type = os.environ.get('LOG_TYPE')
    if log_type is None:
        # "flat" is the default, nothing specific to configure for this
        log_type = 'flat'

    if(log_type == 'logstash'):
        formatter = LogstashFormatter('logstash')
        # set Logstash formatter for all logging handlers
        [handler.setFormatter(formatter) for handler in app.app.logger.handlers]

    # set socket to send logs to
    # this is to allow multiple processes logging
    socketHandler = logging.handlers.SocketHandler('localhost',
                        logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    socketHandler.setLevel(log_level)

    app.app.logger.addHandler(socketHandler)
    app.app.logger.setLevel(log_level)

    #copy required resources
    with app.app.app_context():
        config = ConfigReader()

        resource_dir = config.getResourceDir()
        src_dir = dirname(dirname(abspath(__file__)))
        try:
            copy_tree(src_dir+'/driver-resources', resource_dir)
            app.app.logger.info('required resources copied to :'+resource_dir)
        except Exception as err:
            app.app.logger.error(str(err))

    k = Kafka(app.app.logger)
    app.add_api('swagger.yaml', arguments={'title': 'ansible resource manager specification.'})

    if(ssl and config.ssl_enabled):
        ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ctx.load_cert_chain(config.ssl_dir + '/tls.crt', config.ssl_dir + '/tls.key')

        app.app.logger.info('driver starting listening on port 8443')
        app.run(port=8443,threaded=False,processes=8,ssl_context=ctx)
    else:
        app.app.logger.info('driver starting listening on port 8080')
        app.run(port=8080,threaded=False,processes=8)
