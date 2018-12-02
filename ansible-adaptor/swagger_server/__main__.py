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


if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = JSONEncoder

    log_level = logging.getLevelName(os.environ.get('LOG_LEVEL'))
    if not log_level:
        log_level = 'INFO'

    # set socket to send logs to
    # this is to allow multiple processes logging
    socketHandler = logging.handlers.SocketHandler('localhost',
                        logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    socketHandler.setLevel(log_level)

    app.app.logger.addHandler(socketHandler)
    app.app.logger.setLevel(log_level)

    #copy required resources
    with app.app.app_context():
        resource_dir = ConfigReader().getResourceDir()
        src_dir = dirname(dirname(abspath(__file__)))
        try:
            copy_tree(src_dir+'/driver-resources', resource_dir)
            app.app.logger.info('required resources copied to :'+resource_dir)
        except Exception as err:
            app.app.logger.error(str(err))

    k = Kafka(app.app.logger)
    app.add_api('swagger.yaml', arguments={'title': 'ansible resource manager specification.'})
    app.app.logger.info('driver starting listening on port 8080')
    app.run(port=8080,threaded=False,processes=8)
