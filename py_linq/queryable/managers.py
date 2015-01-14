__author__ = 'ViraLogic Software'

import inspect
import providers
from providers import *
from py_linq.exceptions import *


class ConnectionManager(object):
    """
    ConnectionManager is used to dynamically determine which database connection to use based on connection string
    """

    @staticmethod
    def get_provider_name(connection_uri):
        """
        Gets provider name from connection uri
        :param connection_uri: connection uri as string
        :return: boolean
        """
        if connection_uri is None:
            raise NullArgumentError("No connection uri")
        connection_split = connection_uri.split(':')
        if ':' not in connection_uri or len(connection_split) != 2:
            raise InvalidArgumentError("{0} is not a valid connection uri".format(connection_uri))
        return connection_split[0]

    @staticmethod
    def find_connections():
        """
        Gets a 'provider_name': connection class dictionary of all possible db connection classes
        :return: dict object
        """
        connections = [
            cls
            for name, cls in inspect.getmembers(providers)
            if inspect.isclass(cls)
            and hasattr(cls, '__provider_name__')
            and issubclass(cls, DbConnectionBase)
        ]
        result = {}
        for cls in connections:
            result.setdefault(getattr(cls, '__provider_name__'), cls)
        return result

    @staticmethod
    def get_connection(connection_string):
        """
        Gets the appropriate connection
        :param connection_string: connection string
        :return: connection object
        """
        provider_name = ConnectionManager.get_provider_name(connection_string)
        try:
            cls = ConnectionManager.find_connections()[provider_name]
        except KeyError:
            raise Exception("Unsupported connection provider")
        return cls(connection_string)


