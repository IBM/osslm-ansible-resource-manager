# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.inline_response2003 import InlineResponse2003
from swagger_server.models.inline_response2004 import InlineResponse2004
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestTopologycontrollerController(BaseTestCase):
    """ TopologycontrollerController integration test stubs """

    def test_topology_deployment_locations_get(self):
        """
        Test case for topology_deployment_locations_get

        get list of deployment locations
        """
        response = self.client.open('/api/v1.0/resource-manager/topology/deployment-locations',
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_topology_deployment_locations_name_get(self):
        """
        Test case for topology_deployment_locations_name_get

        get details of a deployment location
        """
        response = self.client.open('/api/v1.0/resource-manager/topology/deployment-locations/{name}'.format(name='name_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_topology_deployment_locations_name_instances_get(self):
        """
        Test case for topology_deployment_locations_name_instances_get

        search for resource instances of a deployment location
        """
        query_string = [('instanceType', 'instanceType_example'),
                        ('instanceName', 'instanceName_example')]
        response = self.client.open('/api/v1.0/resource-manager/topology/deployment-locations/{name}/instances'.format(name='name_example'),
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_topology_instances_id_get(self):
        """
        Test case for topology_instances_id_get

        get details for a resource instance
        """
        response = self.client.open('/api/v1.0/resource-manager/topology/instances/{id}'.format(id='id_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
