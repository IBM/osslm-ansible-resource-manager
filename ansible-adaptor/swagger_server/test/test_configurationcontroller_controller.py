# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.inline_response2007 import InlineResponse2007
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestConfigurationcontrollerController(BaseTestCase):
    """ ConfigurationcontrollerController integration test stubs """

    def test_configuration_get(self):
        """
        Test case for configuration_get

        Get Resource Manager Configuration.
        """
        response = self.client.open('/api/v1.0/resource-manager/configuration',
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
