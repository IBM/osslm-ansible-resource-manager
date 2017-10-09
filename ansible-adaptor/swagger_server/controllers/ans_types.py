"""
manage resource types

IBM Corporation, 2017, jochen kappel
"""
from pathlib import Path
from swagger_server.models.inline_response2001 import InlineResponse2001
from swagger_server.models.inline_response2002 import InlineResponse2002
from flask import current_app as app

from .ans_driver_config import ConfigReader

class ResourceTypeHandler():
    """
    manages resource types
    """
    def __init__(self):
        self.config = ConfigReader()


    def list_resource_types(self):
        """
        list all types
        """

        pload = []
        resDir = self.config.getResourceDir()

        p = Path(resDir)
        # get directories, directoryname = resource name
        dirList = ([name.name for name in p.iterdir() if name.is_dir()])

        for dir in dirList:
            sp = Path(resDir + '/' + dir)
            subdirList = ([name.name for name in sp.iterdir() if name.is_dir()])
            for sdir in subdirList:
                type = InlineResponse2001(name='resource::' + dir + '::' + sdir, state='PUBLISHED')
                pload.append(type)

        return pload


    def get_resource_type(self, typeName):
        """
        get type details
        """

        rc, rcMsg, fname, version = self.validate_resource_type(typeName)
        if rc != 200:
            return rc, rcMsg, ''

        try:
            with open(self.config.getResourceDir() +'/'+fname+'/'+version+'/'+fname+'.yml') as f:
                rd = f.read()
            f.closed
        except FileNotFoundError:
            app.logger.error('File not found for resource descriptor: ' + self.config.getResourceDir() +'/'+fname+'/'+version+'/'+fname+'.yml')
            return 404, 'resource type ' + typeName + ' not found', ''

        resp200 = InlineResponse2002(descriptor=rd, name=typeName, state='PUBLISHED')
        return 200, '', resp200


    def validate_resource_type(self, resourceType):
        """
        is this a valid resource type name
        """
        rTypeParts = resourceType.split("::", maxsplit=2)
        if len(rTypeParts) == 3:
            resType = rTypeParts[1]
            resVer = rTypeParts[2]
        else:
            app.logger.warning('resource type ' + resourceType + ' not found. Invalid format')
            return 404, 'resource type ' + resourceType + ' not found. Invalid format. Should be resource::name::version','',''

        if not Path(str(self.config.getResourceDir())+ '/' + resType).is_dir():
            app.logger.debug('directory '+ str(self.config.getResourceDir())+'/'+resType + ' does not exist')
            app.logger.warning('resource type ' + resType  + ' not found')
            return 404, 'resource type ' + resType  + ' not found', '', ''
        else:
            if not Path(str(self.config.getResourceDir())+ '/' + resType + '/' + resVer).is_dir():
                app.logger.debug('directory '+  str(self.config.getResourceDir())+'/'+resType+'/'+resVer +' does not exist')
                app.logger.warning('resource type version ' + resVer + ' not found')
                return 404, 'resource type version ' + resVer + ' not found','', ''

        app.logger.debug('resource type validated ok with name: ' + resType + ' and version: ' + resVer)
        return 200, 'ok', resType, resVer
