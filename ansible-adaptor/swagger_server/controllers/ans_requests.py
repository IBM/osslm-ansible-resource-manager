"""
manage resource instance transition requests
IBM Corporation, 2017, jochen kappel
"""

import json
import uuid
from datetime import datetime
import pathlib
from concurrent.futures import ThreadPoolExecutor

from swagger_server.models.inline_response202 import InlineResponse202
from flask import current_app as app

from .ans_driver_config import ConfigReader
from .ans_cassandra import CassandraHandler
from .ans_types import ResourceTypeHandler
from .ans_locations import LocationHandler
from .ans_instances import InstanceHandler
from .ans_handler import Runner
from .ans_exceptions import InstanceNotFoundError

import random
import time


class RequestHandler():
    """
    request handler
    """
    def __init__(self):
        self.config = ConfigReader()
        app.logger.debug('initializing request handler')
        self.dbsession = CassandraHandler().get_session()


    def start_request(self, tr):
        """
        start a request i.e. run an ansible playbook_dir
        """
        self.transitionRequest = tr
        # create request id
        self.requestId = uuid.uuid4()
        self.startedAt = datetime.now()

        # do some checks
        app.logger.info('transition request ' + str(self.requestId)  + ' received: ' + str(self.transitionRequest))

        # check resource type
        app.logger.debug('validating request resource type: ' + self.transitionRequest.resource_type)
        rc, rcMsg, self.resType, self.resVer = ResourceTypeHandler().validate_resource_type(self.transitionRequest.resource_type)

        self.playbook_dir = self.config.getResourceDir()+'/'+self.resType+'/'+self.resVer+'/lifecycle/'
        if rc != 200:
            app.logger.error('invalid resource type: ' + self.transitionRequest.resource_type +', ' + rcMsg)
            resp = InlineResponse202(str(self.requestId), 'FAILED', rcMsg, '', self.config.getSupportedFeatures())
            app.logger.info('request ' + str(self.requestId) + ' FAILED: ' + rcMsg)
            return rc, resp

        # check requested action
        action = self.transitionRequest.transition_name
        p = pathlib.Path(self.playbook_dir + action + '.yml')
        if not p.is_file():
            resp = InlineResponse202(str(self.requestId), 'FAILED',
                                     'No playbook found for operation'+self.transitionRequest.transition_name,
                                     'RESOURCE_NOT_FOUND',
                                     self.config.getSupportedFeatures())
            return 404, resp

        # check location exists
        app.logger.debug('validate location: ' + self.transitionRequest.deployment_location)
        rc, rcMsg, location = LocationHandler().get_location_config(self.transitionRequest.deployment_location)
        if rc != 200:
            app.logger.error('location ' + self.transitionRequest.deployment_location + ' ' + rcMsg)
            resp = InlineResponse202(str(self.requestId), 'FAILED', rcMsg, '', self.config.getSupportedFeatures() )
            app.logger.info('request ' + str(self.requestId) + ' FAILED: ' + rcMsg)
            return rc, resp

        # get ansible playbook variables
        # first add location credentials and properties
        user_data = {}
        user_data['user_id'] = 'ALM'
        user_data['keys_dir'] = self.config.getKeysDir()
        user_data['metric_key'] = self.transitionRequest.metric_key
        user_data['request_id'] = self.requestId
        # add properties from the request
        if self.transitionRequest.properties:
            user_data.update(self.transitionRequest.properties)

        # for operations get properties from DB
        #        if action not in ('Install', 'Configure', 'Start', 'Stop', 'Uninstall'):
        if action not in ('Install'):
            app.logger.info('adding lifecycle properties  ')
            try:
                lc_props, lc_intprops = InstanceHandler( self.resType, self.resVer, self.transitionRequest.deployment_location  ).get_instance_properties( self.transitionRequest.metric_key )
            except InstanceNotFoundError as e:
                app.logger.error('Resource NOT FOUND')
                resp = InlineResponse202(str(self.requestId), 'FAILED',
                                         e.msg, 'RESOURCE_NOT_FOUND',
                                         self.config.getSupportedFeatures())
                return 404, resp
            except Exception as e:
                # handle instance not found and any other exception
                app.logger.error(str(e))
                lc_intprops={}
                lc_props={}

            if lc_props:
                lc_props.update(user_data)
                user_data.update(lc_props)

        else:
            lc_intprops={}

        app.logger.info('transition request ' + action + ' variables: ' + str(user_data))

        # creata ansible playbook runner
        runner = Runner(
            hostnames='localhost',
            action=action,
            playbook=self.playbook_dir + action + '.yml',
            private_key_file='',
            become_pass='',
            run_data=user_data,
            internal_data=lc_intprops,
            location=location,
            request_id=self.requestId,
            started_at=self.startedAt,
            config=self.config,
            dbsession=self.dbsession,
            tr=self.transitionRequest,
            verbosity=4
        )

        app.logger.debug('ansible async playbook start')

        # with app.app_context():
        #     timeDelay = random.randrange(2000, 20000)
        #     time.sleep(timeDelay/1000)
        #     executor = ThreadPoolExecutor(max_workers=20)
        #     executor.submit(runner.run_async)
        runner.run_async()

        app.logger.debug('request ' + str(self.requestId) + ' PENDING ')
        resp = InlineResponse202(str(self.requestId), 'PENDING', '','',self.config.getSupportedFeatures())
        return 202, resp

    def get_request(self, requestId):
        """
        get request from db
        """

        pload = {}
        app.logger.debug('reading request status from db')

        if requestId:
            requestId = uuid.UUID(requestId)
        else:
            app.logger.error('request id missing')
            return 400, 'must provide request id', ''

        app.logger.debug('request fetched from DB: ' + str(requestId))
        query = "SELECT requestId, requestState, requestStateReason, requestFailureCode, resourceId, startedAt, finishedAt FROM requests WHERE requestId = %s"
        rows = self.dbsession.execute(query, [requestId])

        if rows:
            pload = {}
            for row in rows:
                pload['requestId'] = str(requestId)
                pload['startedAt'] = row['startedat'].strftime('%Y-%m-%dT%H:%M:%SZ')
                pload['requestStateReason'] = row['requeststatereason']
                pload['requestFailureCode'] = row['requestfailurecode']
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
            app.logger.warning('no request found for id: '+str(requestId))
            return 404, '', ''
