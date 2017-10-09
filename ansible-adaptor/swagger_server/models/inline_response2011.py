# coding: utf-8

from __future__ import absolute_import
from swagger_server.models.inline_response2011_context import InlineResponse2011Context
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class InlineResponse2011(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, request_id: str=None, request_state: str=None, resource_id: str=None, started_at: date=None, finished_at: date=None, context: InlineResponse2011Context=None):
        """
        InlineResponse2011 - a model defined in Swagger

        :param request_id: The request_id of this InlineResponse2011.
        :type request_id: str
        :param request_state: The request_state of this InlineResponse2011.
        :type request_state: str
        :param resource_id: The resource_id of this InlineResponse2011.
        :type resource_id: str
        :param started_at: The started_at of this InlineResponse2011.
        :type started_at: date
        :param finished_at: The finished_at of this InlineResponse2011.
        :type finished_at: date
        :param context: The context of this InlineResponse2011.
        :type context: InlineResponse2011Context
        """
        self.swagger_types = {
            'request_id': str,
            'request_state': str,
            'resource_id': str,
            'started_at': date,
            'finished_at': date,
            'context': InlineResponse2011Context
        }

        self.attribute_map = {
            'request_id': 'requestId',
            'request_state': 'requestState',
            'resource_id': 'resourceId',
            'started_at': 'startedAt',
            'finished_at': 'finishedAt',
            'context': 'context'
        }

        self._request_id = request_id
        self._request_state = request_state
        self._resource_id = resource_id
        self._started_at = started_at
        self._finished_at = finished_at
        self._context = context

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse2011':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_201_1 of this InlineResponse2011.
        :rtype: InlineResponse2011
        """
        return deserialize_model(dikt, cls)

    @property
    def request_id(self) -> str:
        """
        Gets the request_id of this InlineResponse2011.

        :return: The request_id of this InlineResponse2011.
        :rtype: str
        """
        return self._request_id

    @request_id.setter
    def request_id(self, request_id: str):
        """
        Sets the request_id of this InlineResponse2011.

        :param request_id: The request_id of this InlineResponse2011.
        :type request_id: str
        """

        self._request_id = request_id

    @property
    def request_state(self) -> str:
        """
        Gets the request_state of this InlineResponse2011.

        :return: The request_state of this InlineResponse2011.
        :rtype: str
        """
        return self._request_state

    @request_state.setter
    def request_state(self, request_state: str):
        """
        Sets the request_state of this InlineResponse2011.

        :param request_state: The request_state of this InlineResponse2011.
        :type request_state: str
        """
        allowed_values = ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED", "FAILED"]
        if request_state not in allowed_values:
            raise ValueError(
                "Invalid value for `request_state` ({0}), must be one of {1}"
                .format(request_state, allowed_values)
            )

        self._request_state = request_state

    @property
    def resource_id(self) -> str:
        """
        Gets the resource_id of this InlineResponse2011.

        :return: The resource_id of this InlineResponse2011.
        :rtype: str
        """
        return self._resource_id

    @resource_id.setter
    def resource_id(self, resource_id: str):
        """
        Sets the resource_id of this InlineResponse2011.

        :param resource_id: The resource_id of this InlineResponse2011.
        :type resource_id: str
        """

        self._resource_id = resource_id

    @property
    def started_at(self) -> date:
        """
        Gets the started_at of this InlineResponse2011.

        :return: The started_at of this InlineResponse2011.
        :rtype: date
        """
        return self._started_at

    @started_at.setter
    def started_at(self, started_at: date):
        """
        Sets the started_at of this InlineResponse2011.

        :param started_at: The started_at of this InlineResponse2011.
        :type started_at: date
        """

        self._started_at = started_at

    @property
    def finished_at(self) -> date:
        """
        Gets the finished_at of this InlineResponse2011.

        :return: The finished_at of this InlineResponse2011.
        :rtype: date
        """
        return self._finished_at

    @finished_at.setter
    def finished_at(self, finished_at: date):
        """
        Sets the finished_at of this InlineResponse2011.

        :param finished_at: The finished_at of this InlineResponse2011.
        :type finished_at: date
        """

        self._finished_at = finished_at

    @property
    def context(self) -> InlineResponse2011Context:
        """
        Gets the context of this InlineResponse2011.

        :return: The context of this InlineResponse2011.
        :rtype: InlineResponse2011Context
        """
        return self._context

    @context.setter
    def context(self, context: InlineResponse2011Context):
        """
        Sets the context of this InlineResponse2011.

        :param context: The context of this InlineResponse2011.
        :type context: InlineResponse2011Context
        """

        self._context = context

