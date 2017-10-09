"""
Resrouce manager utilities

IBM Corporation, 2017, jochen kappel
"""
import connexion
from swagger_server.models.deployment_location import DeploymentLocation
from swagger_server.models.inline_response201 import InlineResponse201
from flask import abort
from flask import current_app as app
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

from .ans_locations import LocationHandler
from .ans_cassandra import CassandraHandler

def database_delete():
    """
    deletes all database tables
    deletes database tables (intances, resources, locations) !!!

    :rtype: None
    """


    rcode = CassandraHandler().delete_tables()
    if rcode == 200:
        return 200
    else:
        abort(rcode, '')

def database_post():
    """
    create database tables
    creates all required database tables (intances, resources, locations)

    :rtype: None
    """
    rcode =  CassandraHandler().create_tables()
    if rcode == 201 :
        return 201
    else:
        abort(rcode, '')


def database_table_patch(table):
    """
    truncates a given database table
    deletes all content from a database table (intances, resources, locations !!)
    :param table: Table (instances, resources, locations)
    :type table: str

    :rtype: None
    """
    rcode = CassandraHandler().truncate_table(table)
    if rcode == 200:
        return 200
    else:
        abort( rcode, '' )


def topology_deployment_locations_name_delete(name):
    """
    delete a deployment location
    Deletes the specified deployment location
    :param name: Unique name for the location
    :type name: str

    :rtype: None
    """
    app.logger.info('delete location request received')

    loch = LocationHandler()
    rcode, rcMsg = loch.delete_location(name)

    if rcode == 200:
        return 200
    else:
        abort(rcode, rcMsg)


def topology_deployment_locations_name_put(name, deploymentLocation):
    """
    create or update a deployment location
    Returns information for the specified deployment location
    :param name: Unique name for the location
    :type name: str
    :param deploymentLocation:
    :type deploymentLocation: dict | bytes

    :rtype: InlineResponse201
    """
    if connexion.request.is_json:
        deploymentLocation = DeploymentLocation.from_dict(connexion.request.get_json())

    app.logger.info('create location request received')
    app.logger.debug(str(deploymentLocation))

    loch = LocationHandler()
    rcode, rcMsg = loch.create_location(name, deploymentLocation)

    if rcode == 200:
        app.logger.info('location '+name+' created')
        return
    else:
        app.logger.info('location '+name+' not created: ' +rcMsg)
        abort( rcode, rcMsg )


    return InlineResponse201(name, deploymentLocation['type'], deploymentLocation['properties'])
