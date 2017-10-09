import connexion
from swagger_server.models.inline_response200 import InlineResponse200
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime

# business logic imports
from flask import abort
from .ans_driver_config import ConfigReader

def configuration_get():
    """
    Get Resource Manager Configuration.
    Returns high-level information about the configuration of this Resource Manager.

    :rtype: InlineResponse200
    """

    try:
        cfg = ConfigReader()
        drvName, drvVer = cfg.getDriverNameVersion()
        supportedFeatures = cfg.getSupportedFeatures()
        supportedApiVersions = cfg.getSupportedApiVersions()
        supportedProperties = cfg.getDriverProperties()[0]
        supportedProperties.update(cfg.getDriverProperties()[1])
    except FileNotFoundError:
        abort(404, 'configuration not found')


    resp200 = InlineResponse200(drvName, drvVer, supportedApiVersions, supportedFeatures, supportedProperties)
    return resp200
