# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.inline_response2008 import InlineResponse2008  # noqa: E501
from swagger_server.models.inline_response2009 import InlineResponse2009  # noqa: E501
from swagger_server.test import BaseTestCase


class TestTypeControllerController(BaseTestCase):
    """TypeControllerController integration test stubs"""

    def test_types_get(self):
        """Test case for types_get

        Get list of supported resource types
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/types',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_types_name_get(self):
        """Test case for types_name_get

        Get descriptor of a resource types
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/types/{name}'.format(name='name_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
