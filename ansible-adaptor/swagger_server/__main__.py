#!/usr/bin/env python3
"""
ansible resource manager for ALM v1.1

IBM Corporation, 2017, jochen kappel
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from distutils.dir_util import copy_tree
from os.path import dirname, abspath
import connexion
from .encoder import JSONEncoder
from .controllers.ans_driver_config import ConfigReader

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = JSONEncoder

    log_level = logging.getLevelName(os.environ.get('LOG_LEVEL'))
    if not log_level:
        log_level = 'INFO'
    log_dir = os.environ.get('LOG_FOLDER')
    if not log_dir:
        log_dir = '.'
    else:
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir, exist_ok=True)


    # this is set by the dockerfile
    formatter = logging.Formatter("[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = TimedRotatingFileHandler(log_dir + '/almAnsibleDriverLog', when='midnight', interval=1, backupCount=7)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    app.app.logger.addHandler(handler)
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

    app.add_api('swagger.yaml', arguments={'title': 'ansible resource manager specification.'})
    app.app.logger.info('driver starting listening on port 8080')
    app.run(port=8080,threaded=False,processes=8)
