class CommandError(Exception):
    pass


class BaseException(Exception):
    message = 'Unknown Error'

    def __init__(self, code, message=None, details=None, request_id=None,
                 url=None, method=None):
        self.code = code
        self.message = message or self.__class__.message
        self.details = details
        self.request_id = request_id
        self.url = url
        self.method = method

    def __str__(self):
        formatted_string = "%s (HTTP %s)" % (self.message, self.code)
        if self.request_id:
            formatted_string += " (Request-ID: %s)" % self.request_id

        return formatted_string


class BadRequest(BaseException):
    """
    HTTP 400 - Bad request: you sent some malformed data.
    """
    http_status = 400
    message = "Bad request"


class NotFound(BaseException):
    """
    HTTP 404 - Not found
    """
    http_status = 404
    message = "Not found"


class InternalServerError(BaseException):
    """
    HTTP 500 - Internal Server Error
    """
    http_status = 500
    message = "Internal Server Error"


_error_classes = [BadRequest, NotFound, InternalServerError]
_code_map = dict((c.http_status, c) for c in _error_classes)


def from_response(response, body, url, method=None):
    kwargs = {
        'code': response.status_code,
        'method': method,
        'url': url,
        'request_id': None,
    }

    if response.headers:
        kwargs['request_id'] = response.headers.get('x-compute-request-id')

    if body:
        message = "n/a"
        details = "n/a"

        if hasattr(body, 'keys'):
            error = body[list(body)[0]]
            message = error.get('message')
            details = error.get('details')

        kwargs['message'] = message
        kwargs['details'] = details

    cls = _code_map.get(response.status_code, BaseException)
    return cls(**kwargs)
