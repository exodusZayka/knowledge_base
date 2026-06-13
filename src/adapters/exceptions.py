class HttpClientException(Exception):
    """ All exceptions related to http requests. """


class GoogleSearchException(HttpClientException):
    """ Base exception related to the Google search adapter. """
