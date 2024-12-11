# encoding=utf-8
# created @2024/12/10
# created by zhanzq
#

import aiofiles
from utils import check_port_in_use
from sanic import Sanic, request, response
from views.log_analysis_view import LogAnalysisView


# 创建一个 Sanic 实例对象, Sanic 是 web 服务的入口类, 它等价于 flask.Flask
# 然后里面传递一个字符串, 为我们的应用起一个名字
app = Sanic("sanic_service")

# 配置表态文件目录
app.static("/static", "./static")

# app.config 是一个 Config 对象, 可以存储相应的配置, 有以下几种加载方式
# 当然这里也有一个约定，就是配置的名称要大写，但这无关紧要。
app.config.user_name = "古明地觉"  # 通过属性查找的方式设置
app.config["password"] = "地灵殿"  # 通过字典的方式设置
app.config.update_config({"gender": "female", "sister": "古明地恋"})  # 使用 update 的方式, 字节传入一个字典



# 这里通过 @app.get("路由") 的方式和一个视图函数进行绑定
# 视图函数中的 request 参数会接收一个 sanic.request.Request 实例对象, 它包含了接收到的请求中的所有信息
# 比如我们想获取 url 中的查询参数, 那么就需要通过这里的 request 获取, 这个参数在请求到来时会自动传递
@app.get("/index")
async def index(request: request.Request):
    # 这个参数我们暂时先不用, 但是一定要有
    # 这里直接返回一个字符串
    lst = []
    lst.append(f"请求的url: {request.url}")
    lst.append(f"请求的path: {request.path}")
    lst.append(f"请求的方法: {request.method}")
    lst.append(f"请求的查询参数: {request.query_args}")
    lst.append(f"请求的查询参数: {request.args}")
    lst.append(f"a: {request.args.get('a')}, "
               f"b: {request.args.get('b')}, "
               f"a_lst: {request.args.getlist('a')}, "
               f"c: {request.args.get('c')}, "
               f"c: {request.args.get('c', 'xxx')}")
    return response.text("\n".join(lst))


@app.get("/text")
async def text(request: request.Request):
    # 里面传入一个字符串即可, 至于状态码、响应头可以根据自身需求决定是否设置
    return response.text("text")


@app.get("/json")
async def json(request: request.Request):
    # 第一个参数传入一个字典即可
    return response.json({"name": "古明地觉", "age": 16}, ensure_ascii=False)

@app.get("/html")
async def html(request: request.Request):
    # 里面也接收一个字符串, 如果是文件的话, 可以先读取出来
    # 当然还可以使用 jinja2 进行渲染
    return response.html("<h3>古明地觉</h3>")

@app.get("/stream")
async def stream(request: request.Request):
    # Sanic 返回流数据给浏览器, 不是一次性把所有数据返回, 而是一部分一部分地返回
    # 参数如下:
    """
    streaming_fn: 用于写流响应数据的协程函数
    status: 状态码, 默认 200
    headers: 自定义的 http 响应头
    content_type: 默认是纯文本的 content_type, 可以根据实际情况进行修改
    """
    # 定义协程函数
    async def streaming_fn(res):
        await res.write("你好呀\n")
        import asyncio
        await asyncio.sleep(3)
        await res.write("古明地觉")
    # 但是浏览器访问的时候, 并不是先看到 "你好呀\n", 然后 3s 后看到 "古明地觉"
    # 而是 3s 之后一起显示, 因为浏览器上面一旦显示内容, 就代表这一次请求已经结束了
    # 所以是整体一起显示的
    return response.stream(streaming_fn)


@app.get("/file_stream")
async def file_stream(request: request.Request):
    # 从名字上看, 这是 file 和 stream 的结合
    # file_stream 也是返回文件, 但它是一边读一边返回, 每次返回一定大小的数据
    # 而 file 则是一次性返回所有数据, 很明显当文件过大时, file_stream 可以大大节省内存
    """
    参数相比 response.file 会多一个 chunk_size, 表示每次读取的文件数据大小, 默认 4096
    如果是 file_stream, 你会发现响应头中少了 Content-Length, 因为流的形式每次只是返回一个 chunk, 无法得知整个文件的大小
    但是多了一个 Transfer-Encoding
    """
    return await response.file_stream("/Users/zhanzq/Documents/湛子衿学习资料/古诗词/每周古诗/每周古诗--20241110.docx",
                                      mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                      headers={"Content-Disposition": "inline; filename=每周古诗--20241110.docx"})


@app.get("/redirect")
async def redirect(request: request.Request):
    # 会跳转到路由 /text
    return response.redirect("/text")


@app.get("/file")
async def file(request: request.Request):
    # 由于调用 response.file 会得到一个协程, 因此我们需要使用 await
    # 接收如下参数:
    """
    location: 要返回的文件的路径, 必传参数
    status: 成功响应时的 http 状态码 200, 正常返回的话无需修改
    mime_type: 如果为空, 内部会通过 mimetypes 模块的 guess_type 函数进行推断
    headers: 自定义 http 响应头
    filename: 文件名, 如果传递了会写入到响应头 headers 的 Content-Disposition 中
    """
    return await response.file("main.py", mime_type="text/plain; charset=utf-8")


@app.route("/", methods=["POST", "GET"])
async def home(request: request.Request):
    # 如果是 get 请求直接渲染表单页面
    if request.method == "GET":
        return response.html(
            await (await aiofiles.open("index.html", encoding="utf-8")).read()
        )


@app.route("/test", methods=["POST"])
async def test(request: request.Request):
    # 直接通过 request.json 即可获取相应的数据, 会得到一个字典
    json = request.form
    return response.text(f"keys: {tuple(json.keys())}, values: {tuple(json.values())}")


@app.post("/upload")
async def upload_file(request: request.Request):
    files = request.files
    # 得到的是一个 request.File 对象, 它是一个 namedtuple
    # 只有三个成员: "type", "body", "name", 显然代表的含义不需要我多说
    file_names = list(files.keys())
    file_upload = files.get(file_names[0])
    return response.text(f"上传的文件名: {file_upload.name}, 文件内容: {str(file_upload.body, 'utf-8')}, 文件类型: {file_upload.type}")


@app.get("/book/<book_id>")
async def book_info(request: request.Request, book_id):
    books = {"python": "这是 Python 书籍",
            "golang": "这是 Golang 书籍",
            "c": "这是 C 书籍"}
    if (book := books.get(book_id.lower())) is not None:
        res = book
    else:
        res = "不存在此书籍"
    return response.text(res)


@app.route("/login", methods=["GET", "POST"])
async def login(request: request.Request):
    # 如果是 get 请求直接渲染表单页面
    if request.method == "GET":
        return response.html(
            await (await aiofiles.open("login.html", encoding="utf-8")).read()
        )
    # 如果是 post 请求, 则获取表单参数
    elif request.method == "POST":
        # 我们可以通过 request.form 拿到请求的表单内容, 返回的也是一个 RequestParameters 对象
        # 如果多个 input 标签设置了相同的 name, 那么也可以通过 getlist 获取一个列表
        # 不过这种情况不多见
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "23001141" and password == "aaa":
            return response.html("<h3>欢迎来到古明地觉的避难小屋</h3>")
        else:
            return response.html("<h3>用户名或密码错误</h3>")


@app.get("/cookie")
async def cookie(request: request.Request):
    res = response.text("text")
    # 获取 cookie
    print(request.cookies.get("name"))

    # 设置完 cookie 之后再返回，使用max_age指定 cookie 存活的秒数
    res.cookies.add_cookie(key="name", value="古明地觉", max_age=5)

    print(res.cookies.get("name"))
    """
    expire(类型：datetime)：cookie在客户端的浏览器到期时间
    path(类型：string)：cookie应用的URL子集。默认为/
    comment(类型：string)：注释(metadata)
    domain(类型：string)：指定cookie有效的域, 明确指定的域必须始终以点开头
    max-age(类型：数字)：cookie存活的秒数
    secure(类型：boolean)：指定cookie是否只通过HTTPS发送
    httponly(类型：boolean)：指定cookie是否能被Javascript读取
    """

    # 删除 cookie, 直接 del 即可
    # del res.cookies["name"]
    return res

# Register the view with the app
app.add_route(LogAnalysisView.as_view(), '/log_analysis')


# host: 监听的IP, port: 监听的端口, auto_reload: 修改代码之后是否自动重启
def main():
    port = 8809
    try:
        check_port_in_use(port)
        app.run(host="127.0.0.1", port=port, auto_reload=True, debug=True)  # debug=True，开启调试模式
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
