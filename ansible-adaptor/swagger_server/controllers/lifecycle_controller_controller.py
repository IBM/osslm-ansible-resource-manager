import connexion
from swagger_server.models.inline_response2011 import InlineResponse2011
from swagger_server.models.inline_response2005 import InlineResponse2005
from swagger_server.models.inline_response2011_context import InlineResponse2011Context
from swagger_server.models.transition_request import TransitionRequest
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


from .ans_requests import RequestHandler
from flask import abort
from flask import current_app as app
import json, uuid



def lifecycle_transitions_id_status_get(id):
    """
    get details on transition request status
    Returns information about the specified transition or operation request
    :param id: Unique id for the transition request
    :type id: str

    :rtype: InlineResponse2005
    """

    rI = RequestHandler( )
    app.logger.info('getting request status for :' + id)

    try:
        val = uuid.UUID(id)
    except ValueError:
        app.logger.error('id ' + id + ' is not a valid UUID' )
        abort (400, 'not a valid UUID')

    rc, rcMsg, resp200 = rI.get_request( id )

    if ( rc != 200):
        app.logger.error('request ' + id + ': ' + rcMsg)
        abort( rc, rcMsg )
    else:
        app.logger.debug('request ' + id + 'details: ' + json.dumps(resp200))
        return resp200



def lifecycle_transitions_post(transitionRequest=None):
    """
    Performs a transition against a Resource.
    Requests this Resource Manager performs a specific transition against a resource
    :param transitionRequest:
    :type transitionRequest: dict | bytes

    :rtype: InlineResponse2011
    """
    if connexion.request.is_json:
        transitionRequest = TransitionRequest.from_dict(connexion.request.get_json())
    #app.logger.debug('transition request received: ' + transitionRequest)

    # create the request
    app.logger.info('working on transition request ')
    requestHandler = RequestHandler( )
    rc, resp = requestHandler.start_request( transitionRequest )

    if ( rc == 202 ):
        app.logger.info('transition started')
    else:
        app.logger.info('transition start failed')
    #app.logger.debug('transition request response: ' + json.dumps(resp))

    return resp, rc
