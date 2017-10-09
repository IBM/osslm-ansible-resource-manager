### IBM, 2017, jochen kappel
### handles resoruce type requests

import connexion
from swagger_server.models.inline_response2001 import InlineResponse2001
from swagger_server.models.inline_response2002 import InlineResponse2002
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

# business logic imports
from flask import abort
from flask import current_app as app
from .ans_types import ResourceTypeHandler


def types_get():
    """
    Get list of supported resource types
    Returns a list of all resource types managed by this Resource Manage

    :rtype: List[InlineResponse2001]
    """
    app.logger.info('getting type list')
    types = ResourceTypeHandler()
    resp200 = types.list_resource_types()

    if ( resp200 != '' ):
        return resp200
    else:
        app.logger.warning('No types found')
        abort(404, 'no typesfound')


def types_name_get(name):
    """
    Get descriptor of a resource types
    Returns information about a specific resource type, including its YAML descriptor.
    :param name: Unique name for the resource type requested
    :type name: str

    :rtype: List[InlineResponse2002]
    """
    app.logger.info('getting type details')
    resourceType = ResourceTypeHandler()
    rc, rcMsg, resp200 = resourceType.get_resource_type( name )

    if ( rc != 200 ):
        app.logger.warning( rcMsg )
        abort ( rc, rcMsg )
    else:
        return resp200
