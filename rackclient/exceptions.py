# Copyright (c) 2014 ITOCHU Techno-Solutions Corporation.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


class UnsupportedVersion(Exception):
    """Indicates that the user is trying to use an unsupported
    version of the API.
    """
    pass


class CommandError(Exception):
    pass


class HTTPException(Exception):
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


class BadRequest(HTTPException):
    """
    HTTP 400 - Bad request: you sent some malformed data.
    """
    http_status = 400
    message = "Bad request"


class NotFound(HTTPException):
    """
    HTTP 404 - Not found
    """
    http_status = 404
    message = "Not found"


class InternalServerError(HTTPException):
    """
    HTTP 500 - Internal Server Error
    """
    http_status = 500
    message = "Internal Server Error"


class RateLimit(HTTPException):
    """
    HTTP 413 - Too much Requests
    """
    http_status = 413
    message = "This request was rate-limited."


_error_classes = [BadRequest, NotFound, InternalServerError, RateLimit]
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

    cls = _code_map.get(response.status_code, HTTPException)
    return cls(**kwargs)


class BaseError(Exception):
    """
    The base exception class for all exceptions except for HTTPException
    based classes.
    """
    pass


class ForkError(BaseError):
    pass


class AMQPConnectionError(BaseError):
    pass


class InvalidDirectoryError(BaseError):
    pass


class InvalidFilePathError(BaseError):
    pass


class InvalidFSEndpointError(BaseError):
    pass


class FileSystemAccessError(BaseError):
    pass


class MetadataAccessError(BaseError):
    pass


class InvalidProcessError(BaseError):
    pass


class ProcessInitError(BaseError):
    pass


class EndOfFile(Exception):
    message = 'EOF'


class NoDescriptor(Exception):
    message = 'Descriptor Not Found'

    def __init__(self, message=None):
        self.message = message or self.__class__.message

    def __str__(self):
        formatted_string = self.message
        return formatted_string


class NoReadDescriptor(NoDescriptor):
    message = 'Read Descriptor Not Found'


class NoWriteDescriptor(NoDescriptor):
    message = 'Write Descriptor Not Found'
