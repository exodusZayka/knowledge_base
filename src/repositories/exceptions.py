class VectorDBException(Exception):
    pass


class CannotCreateDBClientException(VectorDBException):
    pass


class CannotSaveVectorException(VectorDBException):
    pass
