from models.todo import Todo
from routes.routes_basic import (
    redirect,
    current_user,
    login_required,
    html_response, json_response)
from utils import log


def index(request):
    """
    todo 首页的路由函数
    """
    u = current_user(request)
    return html_response('ajax_todo_index.html')


def all(request):
    ts = [t.__dict__ for t in Todo.all()]
    return json_response(ts)


def add(request):

    form = request.json()
    u = current_user(request)

    Todo.add(form, u.id)
    data = dict(
        message='成功添加 todo'
    )
    return json_response(data)


def route_dict():
    d = {
        '/ajax/todo/index': index,
        '/ajax/todo/all': all,
        '/ajax/todo/add': add,
    }
    return d
