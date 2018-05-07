"""
ansibl resource manager exceptions

IBM Corporation, 2018, jochen kappel
"""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InstanceNotFoundError(Error):
    """Raised when an instance not found for given key
    Attributes:
        instance_key -- search key used for search
        msg - failure message
    """

    def __init__(self, instance_key, msg):
        self.instance_key = instance_key
        self.msg = msg
