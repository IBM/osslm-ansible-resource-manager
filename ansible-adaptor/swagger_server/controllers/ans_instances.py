"""
manage resource instances

IBM Corporation, 2017, jochen kappel
"""

import json
import uuid
from datetime import datetime
from flask import current_app as app
from .ans_driver_config import ConfigReader
from .ans_locations import LocationHandler
from .ans_handler import Runner
from .ans_cassandra import CassandraHandler
from .ans_exceptions import InstanceNotFoundError

class InstanceHandler():
    """
    resource instance handler class
    """
    def __init__(self, resType, resVer, location_name):
        self.config = ConfigReader()
        self.resType = resType
        self.resVer = resVer
        self.location_name = location_name
        self.playbook_dir = self.config.getResourceDir()+'/'+self.resType+'/'+self.resVer+'/lifecycle/'

        self.location = {}
        self.reqHandler = {}
        self.transitionRequest = {}
        self.dbsession = CassandraHandler().get_session()

    def get_all_instances(self, instanceName):
        """
        retrive all instances from db
        """
        loc = LocationHandler()
        app.logger.info('validating location ' + self.location_name)
        rc, rcMsg, self.location = loc.get_location_config(self.location_name)
        if rc != 200:
            app.logger.error(rcMsg)
            return rc, rcMsg, ''

        if (self.resType == 'openstack-network') and (instanceName is None):
            app.logger.error('not supported for resource::openstack-network')
            return 404, 'not supported for networks. instanceName missing', ''

        app.logger.info('get openstack networks')
        if (self.resType == 'openstack-network'):
            self.scan_instances(instanceName)

        pload = []
        # search for instances in the inventory folder
        app.logger.info('search for instances ')

        select = """SELECT resourceId as "resourceId",
             resourceName as "resourceName",
             resourceType as "resourceType",
             resourceManagerId as "resourceManagerId",
             deploymentLocation as "deploymentLocation",
             createdAt as "createdAt",
             lastModifiedAt as "lastModifiedAt",
             properties as "properties"
             FROM instances """
        if self.resType == '':
            query = select + " WHERE deploymentLocation = %s"
            rows = self.dbsession.execute(query, [self.location_name])
        else:
            query = select + "WHERE deploymentLocation = %s AND resourceType = %s"
            rows = self.dbsession.execute(query, [self.location_name, 'resource::'+self.resType+'::' + self.resVer])

        # app.logger.debug('found rows: ' + str(len(rows)))
        for row in rows:
            if row['properties'] is None:
                row['properties'] = {}
            else:
                row['properties'] = dict(row['properties'])

            row['resourceId'] = str(row['resourceId'])
            row['createdAt'] = row['createdAt'].strftime('%Y-%m-%dT%H:%M:%SZ')
            row['lastModifiedAt'] = row['lastModifiedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')

            if instanceName is None:
                pload.append(row)
            elif instanceName in row['resourceName']:
                pload.append(row)

        app.logger.info(str(len(pload)) + ' instances found')
        app.logger.debug('instances found: ' + str(pload))
        return 200, 'ok', pload

    def get_instance_properties(self, metricKey):
        """
        get properties of one instance
        """

        app.logger.info('searching for instance with metricKey: ' + metricKey)

        query = """SELECT properties as "properties",
            internalProperties as "internalproperties"
            FROM instances WHERE metricKey = %s"""
        rows = self.dbsession.execute(query, [metricKey])

        if rows:
            for row in rows:
                if row['properties'] is None:
                    row['properties'] = {}
                else:
                    row['properties'] = dict(row['properties'])
                if row['internalproperties'] is None:
                    row['internalproperties'] = {}
                else:
                    row['internalproperties'] = dict(row['internalproperties'])

                app.logger.info('resource instance found')
            app.logger.debug(str(row))
            return row['properties'], row['internalproperties']
        else:
            app.logger.error('no instance found for metric_key: ' + metricKey)
            raise InstanceNotFoundError(metricKey,'no instance found for metricKey')

    def get_instance(self, instanceId):
        """
        get properties of one instance
        need to search all resource type and locations..
        """

        app.logger.info('searching for instance id: ' + instanceId)

        query = """SELECT resourceId as "resourceId",
            resourcename as "resourceName",
            resourcetype as "resourceType",
            resourcemanagerid as "resourceManaerId",
            deploymentlocation as "deploymentLocation",
            createdat as "createdAt",
            lastmodifiedat as "lastModifiedAt",
            properties as "properties",
            toJson(internalResourceInstances) as "internalResourceInstances"
            FROM instances WHERE resourceId = %s"""
        rows = self.dbsession.execute(query, [uuid.UUID(instanceId)])

        if rows:
            for row in rows:
                if row['properties'] is None:
                    row['properties'] = {}
                else:
                    row['properties'] = dict(row['properties'])

                row['internalResourceInstances'] = json.loads(row['internalResourceInstances'])
                row['resourceId'] = str(row['resourceId'])
                row['createdAt'] = row['createdAt'].strftime('%Y-%m-%dT%H:%M:%SZ')
                row['lastModifiedAt'] = row['lastModifiedAt'].strftime('%Y-%m-%dT%H:%M:%SZ')
                app.logger.info('resource instannce found')
            app.logger.debug(str(row))
            return 200, row
        else:
            app.logger.info('no instance found for id: ' + instanceId)
            return 404, ''

    def scan_instances(self, instanceName):
        """
        scan openstack for instances of a given type
        """
        if instanceName:
            app.logger.info('scanning for instance ' + instanceName)
        app.logger.debug('location is ' + str(self.location))
        # get ansible playbook variables
        user_data = {}
        user_data['user_id'] = 'ALM'

        if self.resType == 'openstack-network':
            user_data['network'] = instanceName
            runner = Runner(
                hostnames='localhost',
                playbook=self.playbook_dir + 'GetInstance.yml',
                private_key_file='',
                become_pass='',
                run_data=user_data,
                internal_data={},
                location=self.location,
                request_id='',
                started_at=datetime.now(),
                config=self.config,
                dbsession='',
                tr='SCAN',
                verbosity=0
            )
            app.logger.info('set openstack network fact collector')

        else:
            app.logger.critical('resource type not supported')
            return

        app.logger.info('run openstack facts playbook')
        properties, rcOK = runner.run()
        app.logger.debug('openstack facts found:' + str(properties))

        app.logger.info('create instance records from facts')

        pitem = {}
        pitem['resourceId'] = properties['id']
        pitem['resourceName'] = properties['name']
        pitem['resourceType'] = 'resource::' + self.resType + '::' + self.resVer
        pitem['deploymentLocation'] = self.location_name
        pitem['resourceManagerId'] = self.config.getDriverName()

        if pitem['resourceId']:
            pitem['resourceId'] = uuid.UUID(pitem['resourceId'])
        else:
            pitem['resourceId'] = None

        # a little cheating, need to get this from OS
        created_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        last_modified_at = created_at

        self.dbsession.execute("""
            INSERT INTO instances
            (resourceId, resourceType, resourceName, resourceManagerId, deploymentLocation, createdAt, lastModifiedAt, properties )
            VALUES  ( %s, %s, %s, %s, %s, %s, %s, %s  )
            """,
            (pitem['resourceId'], pitem['resourceType'], pitem['resourceName'], pitem['resourceManagerId'], pitem['deploymentLocation'], created_at, last_modified_at, properties)
            )

        app.logger.info('instance logged to DB: ' + str(pitem['resourceId']))
        app.logger.debug('resource data: ' + str(pitem))

        return
