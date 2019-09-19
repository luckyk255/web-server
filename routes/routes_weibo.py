from models.comment import Comment
from models.user import User
from models.weibo import Weibo
from routes.routes_basic import (
    redirect,
    current_user,
    html_response,
    login_required,
)
from utils import log


def index(request):
    u = current_user(request)
    if request.method == 'GET':
        log('index GET 方法', request.query)
        if request.query == {}:
            user_id = u.id
        else:
            user_id = int(request.query['user_id'])
    elif request.method == 'POST':
        log('index POST 方法', request.form()['user_id'])
        user_id = request.form()
    u = User.one(id=user_id)
    weibos = Weibo.all(user_id=u.id)
    return html_response('weibo_index.html', weibos=weibos, user=u)


def add(request):

    u = current_user(request)
    form = request.form()
    log('add request.form()', form)
    Weibo.add(form, u.id)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def delete(request):
    weibo_id = int(request.query['weibo_id'])
    Weibo.delete(weibo_id)
    cs = Comment.all(weibo_id=weibo_id)
    for c in cs:
        c.delete(id=c.id)
    return redirect('/weibo/index')


def edit(request):
    weibo_id = int(request.query['weibo_id'])
    w = Weibo.one(id=weibo_id)
    log('修改的 web', w, type(w), w.id, w.content)
    return html_response('weibo_edit.html', weibo=w)


def update(request):
    form = request.form()
    log('update data', form)
    weibo_id = int(form['weibo_id'])
    weibo_content = form['content']
    Weibo.update(weibo_id, content=weibo_content)
    return redirect('/weibo/index')


def comment_add(request):
    u = current_user(request)
    form = request.form()
    c = Comment(form)
    c.add(form, u.id)
    log('comment add', c, u, form)
    return redirect('/weibo/index')


def comment_delete(request):
    comment_id = int(request.query['comment_id'])
    Comment.delete(comment_id)
    return redirect('/weibo/index')


def comment_edit(request):
    comment_id = int(request.query['comment_id'])
    c = Comment.one(id=comment_id)
    return html_response('comment_edit.html', comment=c)


def comment_update(request):
    form = request.form()
    comment_id = int(form['comment_id'])
    Comment.update(comment_id, content=form['content'])
    return redirect('/weibo/index')


def weibo_owner_required(route_function):
    def f(request):
        log('weibo_owner_required')
        u = current_user(request)
        id_key = 'weibo_id'
        if id_key in request.query:
            log('id 在 request 中')
            weibo_id = request.query[id_key]
        else:
            weibo_id = request.form()[id_key]
            log('id 不在 request 中')

        w = Weibo.one(id=int(weibo_id))
        if w.user_id == u.id:
            log('不是微博作者', w)
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_owner_required(route_function):
    def f(request):
        log('comment_owner_required')
        u = current_user(request)
        id_key = 'comment_id'
        if id_key in request.query:
            comment_id = request.query[id_key]
        else:
            comment_id = request.form()[id_key]
        c = Comment.one(id=int(comment_id))

        if c.user_id == u.id:
            log('不是评论作者', c)
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_or_weibo_owner_required(route_function):
    def f(request):
        log('comment_or_weibo_owner_required')
        if request.method == 'GET':
            data = request.query
        elif request.method == 'POST':
            data = request.form()
        else:
            raise ValueError('不支持的方法', request.method)

        comment_key = 'comment_id'
        weibo_key = 'weibo_id'
        if comment_key in data:
            c = Comment.one(id=int(data[comment_key]))
            if c is None:
                return redirect('/weibo/index')
            else:
                user_id = c.user_id
        elif weibo_key in data:
            w = Weibo.one(id=int(data[weibo_key]))
            if w is None:
                return redirect('/weibo/index')
            else:
                user_id = w.user_id
        else:
            raise ValueError('不支持的参数', data)

        u = current_user(request)
        if user_id == u.id:
            log('不是评论或者微博的作者', user_id, u.id)
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def route_dict():
    d = {
        '/weibo/index': login_required(index),
        '/weibo/add': login_required(add),
        '/weibo/delete': login_required(weibo_owner_required(delete)),
        '/weibo/edit': login_required(weibo_owner_required(edit)),
        '/weibo/update': login_required(weibo_owner_required(update)),
        # 评论功能
        '/comment/add': login_required(comment_add),
        '/comment/delete': login_required(comment_or_weibo_owner_required(comment_delete)),
        '/comment/edit': login_required(comment_owner_required(comment_edit)),
        '/comment/update': login_required(comment_owner_required(comment_update)),
    }
    return d
