# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.inline_response20013 import InlineResponse20013  # noqa: E501
from swagger_server.models.inline_response202 import InlineResponse202  # noqa: E501
from swagger_server.models.transition_request1 import TransitionRequest1  # noqa: E501
from swagger_server.test import BaseTestCase


class TestLifecycleControllerController(BaseTestCase):
    """LifecycleControllerController integration test stubs"""

    def test_lifecycle_transitions_id_status_get(self):
        """Test case for lifecycle_transitions_id_status_get

        get details on transition request status
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/lifecycle/transitions/{id}/status'.format(id='id_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_lifecycle_transitions_post(self):
        """Test case for lifecycle_transitions_post

        Performs a transition against a Resource.
        """
        transitionRequest = TransitionRequest1()
        response = self.client.open(
            '/api/v1.0/resource-manager/lifecycle/transitions',
            method='POST',
            data=json.dumps(transitionRequest),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
