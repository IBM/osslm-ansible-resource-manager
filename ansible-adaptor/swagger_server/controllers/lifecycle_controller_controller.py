import connexion
from swagger_server.models.inline_response20013 import InlineResponse20013
from swagger_server.models.inline_response202 import InlineResponse202
from swagger_server.models.transition_request import TransitionRequest
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime
from .ans_requests import RequestHandler
from .ans_thread import threadLocal
from flask import abort
from flask import current_app as app
import json
import uuid

def lifecycle_transitions_id_status_get(id):
    """
    get details on transition request status
    Returns information about the specified transition or operation request
    :param id: Unique id for the transition request
    :type id: str

    :rtype: InlineResponse20013
    """

    rI = RequestHandler()
    app.logger.debug('getting request status for :' + id)

    try:
        val = uuid.UUID(id)
    except ValueError:
        app.logger.error('id ' + id + ' is not a valid UUID')
        abort(400, 'not a valid UUID')

    rc, rcMsg, resp200 = rI.get_request(id)

    if (rc != 200):
        app.logger.error('request ' + id + ': ' + rcMsg)
        abort(rc, rcMsg)
    else:
        app.logger.debug('request ' + id + 'details: ' + json.dumps(resp200))
        return resp200

def lifecycle_transitions_post(transitionRequest=None):
    """
    Performs a transition against a Resource.
    Requests this Resource Manager performs a specific transition against a resource
    :param transitionRequest:
    :type transitionRequest: dict | bytes

    :rtype: InlineResponse202
    """
    try:
        if connexion.request.is_json:
            transitionRequest = TransitionRequest.from_dict(connexion.request.get_json())

        threadLocal.set('txnId', connexion.request.headers.get('X-Tracectx-Transactionid', ''))

        # create the request
        requestHandler = RequestHandler()
        rc, resp = requestHandler.start_request(transitionRequest)

        if rc == 202:
            app.logger.debug('Transition request started: ' + str(transitionRequest))
        else:
            app.logger.error('Transition request start failed: ' + str(transitionRequest))
        # app.logger.debug('transition request response: ' + json.dumps(resp))

        return resp, rc
    finally:
        threadLocal.set('txnId', '')
