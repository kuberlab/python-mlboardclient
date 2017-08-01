
class MlboardClientException(Exception):
    """Base Exception for Mlboard client

    To correctly use this class, inherit from it and define
    a 'message' and 'code' properties.
    """
    message = "An unknown exception occurred"
    code = "UNKNOWN_EXCEPTION"

    def __str__(self):
        return self.message

    def __init__(self, message=message):
        self.message = message
        super(MlboardClientException, self).__init__(
            '%s: %s' % (self.code, self.message))


class TimeoutError(MlboardClientException):
    message = "The execution is timed out"


class IllegalArgumentException(MlboardClientException):
    message = "IllegalArgumentException occurred"
    code = "ILLEGAL_ARGUMENT_EXCEPTION"

    def __init__(self, message=None):
        if message:
            self.message = message
