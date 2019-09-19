import json
import socket
import urllib.parse
import threading
from utils import log

from routes.routes_basic import (
    error,
)
from routes.routes_public import route_dict

from routes.routes_todo import route_dict as routes_todo
from routes.routes_ajax_todo import route_dict as routes_ajax_todo
from routes.routes_weibo import route_dict as routes_weibo


class Request(object):
    def __init__(self, raw_data):
        # 只能 split 一次，因为 body 中可能有换行
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        path = parts[1]
        self.path = ""
        self.query = {}
        self.parse_path(path)
        log('请求 path 和 query', self.path, self.query)

        self.headers = {}
        self.cookies = {}
        self.add_headers(h[1:])
        log('请求 headers', self.headers)
        log('请求 cookies', self.cookies)

    def add_headers(self, header):
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            # 浏览器发来的 cookie 只有一个值
            parts = cookies.split('; ')
            for part in parts:
                k, v = part.split('=', 1)
                self.cookies[k] = v

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f

    def json(self):
        data = json.loads(self.body)
        return data

    def parse_path(self, path):
        index = path.find('?')
        if index == -1:
            self.path = path
            self.query = {}
        else:
            path, query_string = path.split('?', 1)
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = arg.split('=')
                query[k] = v
            self.path = path
            self.query = query


def response_for_path(request):
    r = route_dict()
    r.update(routes_todo())
    r.update(routes_ajax_todo())
    r.update(routes_weibo())
    response = r.get(request.path, error)
    return response(request)


def request_from_connection(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        if len(r) < buffer_size:
            return request


def process_connection(connection):
    with connection:
        r = request_from_connection(connection)
        log('http 请求:<\n{}\n>'.format(r.decode()))
        r = r.decode()
        if len(r) > 0:
            request = Request(r)
            response = response_for_path(request)
            index = response.find(b'Content-Type: text/html')
            if index == -1:
                start = response.find(b'\r\n\r\n')
                gif_length = len(response[start:])
                gif_header = response[:start]
                log('http 响应头部: <{}> 内容长度：<{}>'.format(gif_header, gif_length))
            else:
                log("http 响应:<\n{}\n>".format(response.decode()))
            connection.sendall(response)
        else:
            connection.sendall(b'')


def run(host, port):
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        while True:
            connection, address = s.accept()
            log('请求 ip 和 端口 <{}>\n'.format(address))
            t = threading.Thread(target=process_connection, args=(connection,))
            t.start()


if __name__ == '__main__':
    config = dict(
        host='localhost',
        port=3000,
    )
    run(**config)
