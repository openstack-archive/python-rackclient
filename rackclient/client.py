import copy
import json
import logging
import requests
from rackclient import exceptions


class HTTPClient(object):

    def __init__(self, user, tenant_name, rack_url, http_log_debug=False):
        self.user = user
        self.tenant_name = tenant_name
        self.auth_token = ':'.join([self.user, self.tenant_name])
        self.rack_url = rack_url.rstrip('/')
        self.http_log_debug = http_log_debug
        self._logger = logging.getLogger(__name__)

        if self.http_log_debug and not self._logger.handlers:
            ch = logging.StreamHandler()
            self._logger.addHandler(ch)
            self._logger.propagate = False

    def http_log_req(self, method, url, kwargs):
        if not self.http_log_debug:
            return

        string_parts = ['curl -i']
        string_parts.append(" '%s'" % url)
        string_parts.append(' -X %s' % method)

        headers = copy.deepcopy(kwargs['headers'])
        keys = sorted(headers.keys())
        for name in keys:
            value = headers[name]
            header = ' -H "%s: %s"' % (name, value)
            string_parts.append(header)

        if 'data' in kwargs:
            data = json.loads(kwargs['data'])
            string_parts.append(" -d '%s'" % json.dumps(data))
        self._logger.debug("REQ: %s" % "".join(string_parts))

    def http_log_resp(self, resp):
        if not self.http_log_debug:
            return

        if resp.text and resp.status_code != 400:
            try:
                body = json.loads(resp.text)
            except ValueError:
                body = None
        else:
            body = None

        self._logger.debug("RESP: [%(status)s] %(headers)s\nRESP BODY: "
                           "%(text)s\n", {'status': resp.status_code,
                                          'headers': resp.headers,
                                          'text': json.dumps(body)})

    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers']['User-Agent'] = 'python-rackclient'
        kwargs['headers']['Accept'] = 'application/json'
        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']
        kwargs['headers']['X-Auth-Token'] = self.auth_token

        url = self.rack_url + url

        self.http_log_req(method, url, kwargs)

        request_func = requests.request
        resp = request_func(
            method,
            url,
            **kwargs)

        self.http_log_resp(resp)

        if resp.text:
            try:
                body = json.loads(resp.text)
            except ValueError:
                body = None
        else:
            body = None

        if resp.status_code >= 400:
            raise exceptions.from_response(resp, body, url, method)

        return resp, body

    def get(self, url, **kwargs):
        return self.request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self.request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self.request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self.request(url, 'DELETE', **kwargs)
