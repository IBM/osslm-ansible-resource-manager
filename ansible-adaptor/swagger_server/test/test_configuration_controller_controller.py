# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.inline_response2007 import InlineResponse2007  # noqa: E501
from swagger_server.test import BaseTestCase


class TestConfigurationControllerController(BaseTestCase):
    """ConfigurationControllerController integration test stubs"""

    def test_configuration_get(self):
        """Test case for configuration_get

        Get Resource Manager Configuration.
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/configuration',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
