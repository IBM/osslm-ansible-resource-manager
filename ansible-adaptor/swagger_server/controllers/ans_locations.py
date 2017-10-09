"""
manage locations

IBM Corporation, 2017, jochen kappel
"""

from flask import current_app as app
from .ans_driver_config import ConfigReader
from .ans_cassandra import CassandraHandler

class LocationHandler():
    """
    manages lcoation data
    """
    def __init__(self):
        self.config = ConfigReader()
        self.dbsession = CassandraHandler().get_session()

    def list_locations(self):
        """
        list all configure locations
        """
        pload = []

        app.logger.info('retrieving locations')

        query = "SELECT name, type FROM locations"
        rows = self.dbsession.execute(query)

        for row in rows:
            resp = {"name": row['name'], "type": row['type']}
            pload.append(resp)


        if len(pload) > 0:
            return 200, '', pload
        else:
            return 404, 'no locations found', ''


    def create_location(self, name, deploymentLocation):
        """
        creates a location record in cassandra
        """
        app.logger.info('creating a new location: ' + name)


        try:
            self.dbsession.execute("""
                INSERT INTO locations
                (name, type, description, properties )
                VALUES  ( %s, %s, %s, %s  )
                """,
                (name, deploymentLocation.type, '', deploymentLocation.properties)
                )
        except:
            app.logger.error('error creating the location instance ' + name)
            return 400, 'Error creating location '+name


        app.logger.debug(name + '  ' + str(deploymentLocation))
        app.logger.info('location created: ' + name)
        return 200, ''

    def delete_location(self, name):
        """
        creates a location record in cassandra
        """
        app.logger.info('deleting location: ' + name)

        try:
            stmt = "DELETE FROM locations WHERE name = %s"
            self.dbsession.execute(stmt, [name])
        except:
            app.logger.error('error deleting location ' + name)
            return 400, 'Error deleting location '+name

        app.logger.info('location deleted: ' + name)
        return 200, ''


    def get_location(self, locationName):
        """
        get location details
        """

        app.logger.info('retrieving location data for ' + locationName)

        query = "SELECT name, type, properties FROM locations WHERE name = %s"
        rows = self.dbsession.execute(query, [locationName])

        for row in rows:
            app.logger.debug(str(row))
            return 200, '', row

        return 404, 'no location found for ' + locationName, ''


    def get_location_config(self, locationName):
        """
        read location properties
        """

        app.logger.info('getting properties for location ' + locationName)

        rc, rcMsg, location = self.get_location(locationName)

        if rc == 200:
            app.logger.info('location details found')
            if location['properties'] is None:
                locationProps = {}
            else:
                locationProps = dict(location['properties'])
            locationProps['type'] = location['type']
            app.logger.debug('location details: ' + str(locationProps))
            return 200, '', locationProps
        else:
            return rc, rcMsg, ''
