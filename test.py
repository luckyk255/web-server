import pymysql

from models.comment import Comment
from models.todo import Todo
from models.user import User
from models.session import Session
from models.weibo import Weibo
from utils import random_string


def test():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='tk1998',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        cursor.execute('DROP DATABASE `web8`')
        cursor.execute('CREATE DATABASE `web8` CHARACTER SET utf8mb4')
        cursor.execute('USE `web8`')

        cursor.execute(User.sql_create)
        cursor.execute(Session.sql_create)
        cursor.execute(Todo.sql_create)
        cursor.execute(Comment.sql_create)
        cursor.execute(Weibo.sql_create)
    connection.commit()
    connection.close()

    form = dict(
        username='lucky',
        password='1998',
    )
    User.register_user(form)
    u, result = User.login_user(form)
    assert u is not None, result
    form = dict(
        username='test',
        password='123',
    )
    User.register_user(form)

    session_id = random_string()
    form = dict(
        session_id=session_id,
        user_id=u.id,
    )
    Session.new(form)
    s: Session = Session.one(session_id=session_id)
    assert s.session_id == session_id

    form = dict(
        title='test todo',
        user_id=u.id,
    )
    t = Todo.add(form, u.id)
    assert t.title == 'test todo'

    form = dict(
        content='test comment content',
        user_id=u.id,
    )
    c = Comment.add(form, u.id)
    assert c.content == 'test comment content'

    form = dict(
        content='test web content',
        user_id=u.id,
    )
    c = Weibo.add(form, u.id)
    assert c.content == 'test web content'


if __name__ == '__main__':
    test()
