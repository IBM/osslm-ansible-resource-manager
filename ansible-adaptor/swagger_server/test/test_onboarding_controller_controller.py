# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.test import BaseTestCase


class TestOnboardingControllerController(BaseTestCase):
    """OnboardingControllerController integration test stubs"""

    def test_types_upload(self):
        """Test case for types_upload

        Upload VNF packages
        """
        data = dict(resource_name='resource_name_example',
                    resource_version='resource_version_example',
                    upfile=(BytesIO(b'some file data'), 'file.txt'))
        response = self.client.open(
            '/api/v1.0/resource-manager/types',
            method='POST',
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
