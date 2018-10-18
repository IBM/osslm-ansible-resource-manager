# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.deployment_location1 import DeploymentLocation1  # noqa: E501
from swagger_server.models.inline_response20011 import InlineResponse20011  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDriverAdditionsController(BaseTestCase):
    """DriverAdditionsController integration test stubs"""

    def test_database_delete(self):
        """Test case for database_delete

        deletes all database tables
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/database',
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_database_post(self):
        """Test case for database_post

        create database tables
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/database',
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_database_table_patch(self):
        """Test case for database_table_patch

        truncates a given database table
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/database/{table}'.format(table='table_example'),
            method='PATCH')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_topology_deployment_locations_name_delete(self):
        """Test case for topology_deployment_locations_name_delete

        delete a deployment location
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/topology/deployment-locations/{name}'.format(name='name_example'),
            method='DELETE',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_topology_deployment_locations_name_put(self):
        """Test case for topology_deployment_locations_name_put

        create or update a deployment location
        """
        deploymentLocation = DeploymentLocation1()
        response = self.client.open(
            '/api/v1.0/resource-manager/topology/deployment-locations/{name}'.format(name='name_example'),
            method='PUT',
            data=json.dumps(deploymentLocation),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_topology_deployment_locations_properties_get(self):
        """Test case for topology_deployment_locations_properties_get

        get list of deployment locations with all properties
        """
        response = self.client.open(
            '/api/v1.0/resource-manager/topology/deployment-locations/properties',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
