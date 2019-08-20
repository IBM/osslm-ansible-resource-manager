"""
reads config file for the ansible resource manager driver

IBM Corporation, 2017, jochen kappel
"""
import os
import yaml
from flask import current_app as app
from str2bool import str2bool

class ConfigReader:
    """
    singleton to read and cache configuration
    """
    class __ConfigReader:
        """
        inner singleton class
        """
        def __init__(self):
            try:
                with open("./config.yml", 'r') as ymlfile:
                    cfg = yaml.load(ymlfile)
            except FileNotFoundError:
                app.logger.critical('configuration file config.yml not found')
                raise FileNotFoundError

            app.logger.debug('loading configuration')
            self.driver_name = cfg['driver']['name']
            self.driver_version = cfg['driver']['version']
            self.requests_ttl = os.environ.get('cassandra_ttl', None) or cfg['cassandra']['ttl']
            self.cassandra_uri = os.environ.get('cassandra_uri', None) or cfg['cassandra']['uri']
            self.kafka_replicationFactor = os.environ.get('kafka_replicationFactor')
            self.kafka_replicationFactor = int(self.kafka_replicationFactor)
            self.kafka_url = os.environ.get('KAFKA_URL')

            self.resource_dir = os.environ.get('ansible_resource_dir', None) or cfg['ansible']['resource_dir']
            app.logger.debug('check for resource folder: ' + self.resource_dir)
            # check if configured directory exists:
            if not os.path.isdir(self.resource_dir):
                app.logger.warning('resource folder ' + self.resource_dir + ' does not exist')
                app.logger.debug('creating resource folder ' + self.resource_dir)
                os.mkdir(self.resource_dir)

            self.keys_dir = os.environ.get('ansible_keys_dir', None) or cfg['ansible']['keys_dir']
            app.logger.debug('check for keys folder: ' + self.keys_dir)
            # check if configured directory exists:
            if not os.path.isdir(self.keys_dir):
                app.logger.warning('keys folder ' + self.keys_dir + ' does not exist')
                app.logger.debug('creating keys folder ' + self.keys_dir)
                os.mkdir(self.keys_dir)

            tmp = os.environ.get('num_processes', None)
            if tmp is None:
                tmp = cfg['num_processes']
                if tmp is not None:
                    self.num_processes = int(tmp)
                else:
                    self.num_processes = 8
            else:
                self.num_processes = int(tmp)

            tmp = os.environ.get('ssl_enabled', None)
            if(tmp is None):
                tmp = cfg['ssl']['enabled']
            self.ssl_enabled = str2bool(tmp)
            self.ssl_dir = os.environ.get('ssl_dir', None) or cfg['ssl']['dir']

            self.supported_features = cfg['driver']['supportedFeatures']
            self.supported_api_version = cfg['driver']['supportedApiVersions']
            self.supported_properties = cfg['driver']['properties']
            app.logger.debug('config properties ' + str(self.supported_properties) )
            props = {k: v for d in self.supported_properties for k, v in d.items()}
            self.supported_properties=props

        def getDriverNameVersion(self):
            """ get driver name and version """
            return self.driver_name, self.driver_version

        def getDriverName(self):
            """ get driver name """
            return self.driver_name

        def getDriverVersion(self):
            """ get driver version """
            return  self.driver_version

        def getResourceDir(self):
            """ get resource directory """
            return self.resource_dir

        def getKeysDir(self):
            """ get keypair directory """
            return self.keys_dir

        def getKafkaReplicationFactor(self):
            return self.kafka_replicationFactor

        def getKafkaUrl(self):
            return self.kafka_url

        def getDriverProperties(self, property):
            """ get driver properties """
            if property == None:
                return self.supported_properties
            else:
                return os.environ.get('driver_' + property, None) or self.supported_properties[property]

        def getSupportedFeatures(self):
            """ get supported features """
            return self.supported_features

        def getSupportedApiVersions(self):
            """ get supported ALM API version """
            return self.supported_api_version

        def getTTL(self):
            """ get time to live for request records """
            return self.requests_ttl

    instance = None

    def __init__(self):
        if not ConfigReader.instance:
            ConfigReader.instance = ConfigReader.__ConfigReader()

    def __getattr__(self, name):
        return getattr(self.instance, name)
