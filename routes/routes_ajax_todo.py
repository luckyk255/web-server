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
    """
    用于增加新 todo 的路由函数
    """
    form = request.json()
    u = current_user(request)

    Todo.add(form, u.id)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    data = dict(
        message='成功添加 todo'
    )
    return json_response(data)


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/ajax/todo/index': index,
        '/ajax/todo/all': all,
        '/ajax/todo/add': add,
    }
    return d
