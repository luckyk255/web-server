import json

from jinja2 import FileSystemLoader, Environment

from utils import log
from models.user import User
from models.session import Session


def template(name):
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def current_user(request):
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
        u = Session.find_user(session_id=session_id)
        return u
    else:
        return User.guest()


def error(request):
    return b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>'


def response_with_headers(headers, code=200):
    header = 'HTTP/1.x {} VERY OK\r\n'.format(code)
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def redirect(url, result='', headers=None):
    if len(result) > 0:
        formatted_url = '{}?result={}'.format(
            url, result
        )
    else:
        formatted_url = url
    h = {
        'Location': formatted_url,
    }
    if isinstance(headers, dict):
        h.update(headers)

    r = response_with_headers(h, 302) + '\r\n'
    return r.encode()


def html_response(filename, **kwargs):
    headers = {
        'Content-Type': 'text/html',
    }
    header = response_with_headers(headers)
    body = Template.render(filename, **kwargs)
    r = header + '\r\n' + body
    return r.encode()


def json_response(data):
    headers = {
        'Content-Type': 'application/json',
    }
    header = response_with_headers(headers)
    body = json.dumps(data, indent=2, ensure_ascii=False)
    r = header + '\r\n' + body
    return r.encode()


def login_required(route_function):
    
    def f(request):
        log('用户登录权限认证')
        log('login_required', route_function)
        u = current_user(request)
        if u.is_guest():
            log('login_required is_guest', u)
            return redirect('/login/view')
        else:
            return route_function(request)
    return f


def _initialized_environment():
    loader = FileSystemLoader('templates')
    e = Environment(loader=loader)
    return e


class Template:
    env = _initialized_environment()

    @classmethod
    def render(cls, filename, **kwargs):
        t = cls.env.get_template(filename)
        return t.render(**kwargs)
