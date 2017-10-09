# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.inline_response2001 import InlineResponse2001
from swagger_server.models.inline_response2002 import InlineResponse2002
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestTypecontrollerController(BaseTestCase):
    """ TypecontrollerController integration test stubs """

    def test_types_get(self):
        """
        Test case for types_get

        Get list of supported resource types
        """
        response = self.client.open('/api/v1.0/resource-manager/types',
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_types_name_get(self):
        """
        Test case for types_name_get

        Get descriptor of a resource types
        """
        response = self.client.open('/api/v1.0/resource-manager/types/{name}'.format(name='name_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
