# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.inline_response20013 import InlineResponse20013
from swagger_server.models.inline_response202 import InlineResponse202
from swagger_server.models.transition_request1 import TransitionRequest
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestLifecyclecontrollerController(BaseTestCase):
    """ LifecyclecontrollerController integration test stubs """

    def test_lifecycle_transitions_id_status_get(self):
        """
        Test case for lifecycle_transitions_id_status_get

        get details on transition request status
        """
        response = self.client.open('/api/v1.0/resource-manager/lifecycle/transitions/{id}/status'.format(id='id_example'),
                                    method='GET',
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_lifecycle_transitions_post(self):
        """
        Test case for lifecycle_transitions_post

        Performs a transition against a Resource.
        """
        transitionRequest = TransitionRequest()
        response = self.client.open('/api/v1.0/resource-manager/lifecycle/transitions',
                                    method='POST',
                                    data=json.dumps(transitionRequest),
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
