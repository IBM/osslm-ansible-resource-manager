"""
manage resource instance transition requests

IBM Corporation, 2017, jochen kappel
"""

import json
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from swagger_server.models.inline_response202 import InlineResponse202
from flask import current_app as app

from .ans_driver_config import ConfigReader
from .ans_cassandra import CassandraHandler
from .ans_types import ResourceTypeHandler
from .ans_locations import LocationHandler
from .ans_handler import Runner


class RequestHandler():
    """
    request handler
    """
    def __init__(self):
        self.config = ConfigReader()
        app.logger.info('initializing request handler')
        self.dbsession = CassandraHandler().get_session()


    def start_request(self, tr):
        """
        start a request i.e. run an ansible playbook_dir
        """
        self.transitionRequest = tr
        # create request id
        self.requestId = uuid.uuid1()
        app.logger.debug('creating request with id: ' + str(self.requestId))
        self.startedAt = datetime.now()

        # do some checks
        app.logger.info('transition request received')
        app.logger.debug('transition action: ' + self.transitionRequest.transition_name )

        # check resource type
        app.logger.info('validating requeste resource type: ' + self.transitionRequest.resource_type)
        rc, rcMsg, self.resType, self.resVer = ResourceTypeHandler().validate_resource_type(self.transitionRequest.resource_type)

        self.playbook_dir = self.config.getResourceDir()+'/'+self.resType+'/'+self.resVer+'/'

        if rc != 200:
            app.logger.error('invalid resource type: ' + self.transitionRequest.resource_type +', ' + rcMsg)
            resp = InlineResponse202(str(self.requestId), 'FAILED', self.config.getSupportedFeatures())
            app.logger.info('request ' + str(self.requestId) + ' FAILED: ' + rcMsg)
            return rc, resp

        # check location exists
        app.logger.info('validate location: ' + self.transitionRequest.deployment_location)
        rc, rcMsg, location = LocationHandler().get_location_config(self.transitionRequest.deployment_location)
        if rc != 200:
            app.logger.error('location ' + self.transitionRequest.deployment_location + ' ' + rcMsg)
            resp = InlineResponse202(str(self.requestId), 'FAILED', self.config.getSupportedFeatures())
            app.logger.info('request ' + str(self.requestId) + ' FAILED: ' + rcMsg)
            return rc, resp

        # check requested action
        action = self.transitionRequest.transition_name

        # get ansible playbook variables
        app.logger.info('set playbook variables')
        # first add locatino credentials and properties
        user_data = {}
        user_data['user_id'] = 'ALM'
        user_data['keys_dir'] = self.config.getKeysDir()
        # add properties from the request
        if self.transitionRequest.properties:
            user_data.update(self.transitionRequest.properties)
        app.logger.debug('playbook variables set: ' + str(user_data))

        # creata ansible playbook runner
        app.logger.info('create an ansible playbook runner')
        runner = Runner(
            hostnames='localhost',
            playbook=self.playbook_dir + action + '.yml',
            private_key_file='',
            become_pass='',
            run_data=user_data,
            location=location,
            request_id=self.requestId,
            started_at=self.startedAt,
            config=self.config,
            dbsession=self.dbsession,
            tr=self.transitionRequest,
            verbosity=1
        )

        app.logger.info('ansible async playbook start')

        with app.app_context():
            executor = ThreadPoolExecutor(max_workers=4)
            executor.submit(runner.run_async)

            app.logger.info('request ' + str(self.requestId) + ' PENDING ')
            resp = InlineResponse202(str(self.requestId), 'PENDING', self.config.getSupportedFeatures())
            return 202, resp

    def get_request(self, requestId):
        """
        get request from db
        """

        pload = {}
        app.logger.info('reading request status from db')

        if requestId:
            requestId = uuid.UUID(requestId)
        else:
            app.logger.error('request id missing')
            return 400, 'must provide request id', ''

        app.logger.info('request fetched from DB: ' + str(requestId))
        query = "SELECT requestId, requestState, requestStateReason, resourceId, startedAt, finishedAt FROM requests WHERE requestId = %s"
        rows = self.dbsession.execute(query, [requestId])

        if rows:
            pload = {}
            for row in rows:
                pload['requestId'] = str(requestId)
                pload['startedAt'] = row['startedat'].strftime('%Y-%m-%dT%H:%M:%SZ')
                pload['requestStateReason'] = row['requeststatereason']
                pload['requestState'] = row['requeststate']
                if row['finishedat'] is not None:
                    pload['finishedAt'] = row['finishedat'].strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    pload['finishedAt'] = ''
                if row['resourceid'] is not None:
                    pload['resourceId'] = str(row['resourceid'])
                else:
                    pload['resourceId'] = ''

            app.logger.debug('request status is: ' + json.dumps(pload))

            return 200, '', pload
        else:
            app.logger.info('no request found for id: '+str(requestId))
            return 404, '', ''
