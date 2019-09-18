var log = console.log.bind(console, new Date().toLocaleString())

var e = function (selector) {
    return document.querySelector(selector)
}

var todoTemplate = function (todo) {
    var t = `
    <div class="todo-cell">
        <span>${todo}</span>
    </div>
    `
    /*
    t = """
    <div class="todo-cell">
        <span>{}</span>
    </div>
    """.format(todo)
     */
    return t
}



/*
1. 给 add button 绑定事件
2. 在事件处理函数中，获取 input 的值
3. 用获取的值，组装一个 todo-cell HTML 字符串
4. 插入 todo-list 中
*/

var insertTodo = function (todoCell) {
    var form = document.querySelector('#id-todo-list')
    form.insertAdjacentHTML('beforeEnd', todoCell)
}

var loadTodos = function () {
    ajax('POST', '/ajax/todo/all', {}, function (json) {
        log('拿到ajax响应')
        log('response data', json)
        for (var i = 0; i < json.length; i++) {
            log('json for', json[i], json)
            var todo = json[i].title
            var todoCell = todoTemplate(todo)
            log(todoCell)
            insertTodo(todoCell)
        }
    })
}

var bindEvents = function () {
    var b = e('#id-button-add')
    b.addEventListener('click', function () {
        log('click')
        var input = e('#id-input-todo')
        log(input)
        log(input.value)
        var todoTitle = input.value
        var todoCell = todoTemplate(todoTitle)
        log(todoCell)

        var data = {
            title: todoTitle
        }
        ajax('POST', '/ajax/todo/add', data, function (json) {
            log('拿到ajax响应')
            var message = json.message
            log('message 类型', typeof(message))
            alert(message)
            insertTodo(todoCell)
        })
    })
}

var main = function () {
    loadTodos()
    bindEvents()
}

main()