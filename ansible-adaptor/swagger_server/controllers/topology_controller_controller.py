import connexion
from swagger_server.models.inline_response2003 import InlineResponse2003
from swagger_server.models.inline_response2004 import InlineResponse2004
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


# business logic imports
import yaml, json, uuid
from flask import abort
from flask import current_app as app
from .ans_types import ResourceTypeHandler
from .ans_instances import InstanceHandler
from .ans_locations import LocationHandler

def topology_deployment_locations_get():
    """
    get list of deployment locations
    Returns a list of all deployment locations available to this Resource Manager

    :rtype: List[InlineResponse2003]
    """

    # get locations from db
    locations = LocationHandler()
    app.logger.info('getting locations')
    rc, rcMsg, resp200 = locations.list_locations()

    if ( rc == 200 ):
        app.logger.debug('locations found ' + str(resp200))
        return resp200
    else:
        abort(rc, rcMsg)


def topology_deployment_locations_name_get(name):
    """
    get details of a deployment location
    Returns information for the specified deployment location
    :param name: Unique name for the location requested
    :type name: str

    :rtype: InlineResponse2003
    """

    location = LocationHandler()
    app.logger.info('getting details for location ' + name)
    rc, rcMsg, resp200 = location.get_location( name )

    if ( rc != 200):
        app.logger.warning('location '+ name + 'not found')
        abort( rc, rcMsg )
    else:
        resp = {'name': name, 'type': resp200['type'] }
        app.logger.debug('found location ' + str(resp))
        return resp


def topology_deployment_locations_name_instances_get(name, instanceType=None, instanceName=None):
    """
    search for resource instances of a deployment location
    Searches for resource instances managed within the specified deployment location. The search can be restricted by the type of the resources to be returned, or a partial match on the name of the resources.
    :param name: Unique name for the deployment location
    :type name: str
    :param instanceType: Limits results to be of this resource type (optional, exact matches only)
    :type instanceType: str
    :param instanceName: Limits results to contain this string in the name (optional, partial matching)
    :type instanceName: str

    :rtype: List[InlineResponse2004]
    """

    location_name = name

    # check if resource type an version exists
    if ( instanceType == None ):
        resVer = ''
        resType = ''
    else:
        val = ResourceTypeHandler()
        app.logger.info('validating Resource Type ' + instanceType)
        rc, rcMsg, resType, resVer = val.validate_resource_type( instanceType )
        if (rc != 200):
            app.logger.error('Wrong resource type '+ instanceType)
            app.logger.debug( instanceType + ': ' + rcMsg )
            abort (rc, rcMsg)

        app.logger.info('Resource type correct, name ' + resType + ' version ' + resVer)


    instances = InstanceHandler( resType, resVer, location_name )
    app.logger.info('Searching instances for location '+ location_name)
    rc, rcMsg, payload = instances.get_all_instances( instanceName )
    if (rc != 200 ):
        app.logger.error('no instance found: ' + rcMsg)
        abort( rc, rcMsg)


    return payload


def topology_instances_id_get(id):
    """
    get details for a resource instance
    Returns information for the specified resource instance
    :param id: Unique id for the resource instance
    :type id: str

    :rtype: InlineResponse2004
    """
    instances = InstanceHandler( '', '', '')
    app.logger.info('getting details for instance: ' + id)

    try:
        val = uuid.UUID(id)
    except ValueError:
        app.logger.error('id ' + id + ' is not a valid UUID' )
        abort (400, 'not a valid UUID')

    rcode, payload = instances.get_instance( id )
    app.logger.debug('instance ' + id + 'details: ' + str(payload))

    if rcode == 200:
        return payload
    else:
        abort( 404,'')
