import os
import sys
import time
from traceback import format_exc

import requests
from flask import *

app = Flask(__name__)

# 记录每个 IP 的请求历史：{ 'IP地址': [时间戳1, 时间戳2...] }
ip_records = {}

# 记录 IP 永久拉黑历史
ip_ban_records = {}

# 记录被永久拉黑的 IP
ban_ip = []

# 加载已保存的 ban ip
try:
    with open('/Users/luojingfeng/html-project/ts-server/ban_ip.txt') as f:
        for line in f:
            ip = line.strip()
            ban_ip.append(ip)
except Exception:
    print(format_exc())


# noinspection inconsistent-returns
@app.before_request
def anti_crawler():
    ip = get_real_ip()
    print(ip)
    if ip in ban_ip:
        return f"You are banned! Because your 429 x 30! ip={ip}", 403

    now = time.time()

    # 如果是新的 IP，初始化一个列表
    if ip not in ip_records:
        ip_records[ip] = []

    # 只保留最近 2 秒内的请求记录
    ip_records[ip] = [t for t in ip_records[ip] if now - t < 2]

    # 如果被429超过30次, 永久拉黑处理!
    if ip in ip_ban_records:
        if len(ip_ban_records[ip]) > 30:
            ban_ip.append(ip)
            try:
                with open('/Users/luojingfeng/html-project/ts-server/ban_ip.txt', 'w') as f:
                    f.write('\n'.join(ban_ip))
            except Exception:
                print(format_exc())

    # 如果 2 秒内请求超过 20 次，直接拉黑拦截
    if len(ip_records[ip]) >= 20:
        if ip not in ip_ban_records:
            ip_ban_records[ip] = []
        ip_ban_records[ip].append(now)
        page = """
        <h1>429 Too Many Requests</h1>
        <h1>请减慢你的刷新速度!</h1>
        """
        return page, 429

    # 记录这次请求的时间
    ip_records[ip].append(now)


def get_real_ip():
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For 可能是 "客户端IP, 代理IP1, 代理IP2"
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


@app.errorhandler(404)
def four_zero_four_not_found(*args):
    return '404 Not Found!', 404


@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


@app.route('/say_room', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_a():
    print(111)
    url = 'http://127.0.0.1:14258/'
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k: v for k, v in request.headers if k != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )
    return Response(resp.content, resp.status_code, resp.headers.items())


@app.route('/say_room/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_b(path):
    print(123)
    url = 'http://127.0.0.1:14258/%s' % path
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k: v for k, v in request.headers if k != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )
    return Response(resp.content, resp.status_code, resp.headers.items())


@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_c(path):
    print(123)
    url = 'http://127.0.0.1:14258/api/%s' % path
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k: v for k, v in request.headers if k != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )
    return Response(resp.content, resp.status_code, resp.headers.items())


@app.route('/mc', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_mc():
    print(222)
    url = 'http://127.0.0.1:23456'
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k: v for k, v in request.headers if k != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )
    return Response(resp.content, resp.status_code, resp.headers.items())


@app.route('/python-rumen')
def python_rumen():
    return send_from_directory('.', 'python-rumen.html')


@app.route('/admin')
def admin_login():
    return send_from_directory('.', 'admin/index.html')


@app.route('/ollamaSetup.exe.download')
def download_ollama_setup_exe():
    return send_from_directory('.', 'ollamaSetup-download.html')


@app.route('/ollamaSetup.exe')
def ollama_setup():
    return send_file('./ollamaSetup.exe', as_attachment=True)


@app.route('/pycharm-download')
def pycharm_download():
    return send_from_directory('.', 'pycharm-download.html')


@app.route('/pycharm-2026.2.3.exe')
def pycharm_2026_exe():
    return send_file('./pycharm-2026.2.3.exe', as_attachment=True)


def teapot_all():
    content_type = request.headers.get('Content-Type', '')
    data = request.get_data(as_text=True)

    if 'coffee' in content_type.lower():
        return Response(
            "I'm a little teapot. Short and stout.",
            status=418,
            mimetype='text/plain'
        )

    if 'tea' in content_type.lower():
        if 'start' in data.lower():
            return Response(
                "started brew tea",
                status=418,
                mimetype='text/plain'
            )
        if 'stop' in data.lower():
            return Response(
                "stopped brew tea",
                status=418,
                mimetype='text/plain'
            )
        return Response(
            "What do you want to do?",
            status=418,
            mimetype='text/plain'
        )

    if 'about' in content_type.lower():
        return Response(
            """
I'm a little teapot, short and stout.
Here is my handle, here is my spout.
When I get all steamed up, hear me shout:
Tip me over and pour me out!
            """,
            status=200,
            mimetype='text/plain'
        )

    return Response(
        "This is a teapot. Try BREW and POST methods and send 'tea' or 'coffee'.",
        status=200,
        mimetype='text/plain'
    )


@app.route('/teapot')
def about_teapot():
    return send_from_directory('.', 'about_teapot.html')


@app.route('/teapot-1', methods=['GET', 'POST', 'BREW'])
def teapot1():
    return teapot_all()


@app.route('/teapot-2', methods=['GET', 'POST', 'BREW'])
def teapot2():
    return teapot_all()


@app.route('/teapot-3', methods=['GET', 'POST', 'BREW'])
def teapot3():
    return teapot_all()


@app.route('/teapot-4', methods=['GET', 'POST', 'BREW'])
def teapot4():
    return teapot_all()


@app.route('/teapot-5', methods=['GET', 'POST', 'BREW'])
def teapot5():
    return teapot_all()


@app.route('/boom')
def boom():
    return send_from_directory('.', 'boom.html')


@app.route('/boom.mp3')
def boom_mp3():
    return send_file('boom.mp3')


@app.route('/class_end_daojishi')
def class_end_daojishi():
    return send_from_directory('.', 'class_end_daojishi.html')


@app.route('/digital-7-mono-subset')
def digital7_mono_subset():
    return send_file('./static/fonts/digital-7-mono-subset.ttf')


@app.route('/GB18030-Bitmap')
def gb18030_bitmap():
    return send_file('./static/fonts/GB18030-Bitmap.ttf')


@app.route('/love-eyes.mp4')
def love_eyes_mp4():
    return send_file('./static/video/love-eyes.mp4')


@app.route('/shared')
def shared():
    return send_from_directory('.', 'share_file/index.html')


@app.route('/share-file/upload', methods=['POST'])
def upload():
    current_path = 'html-project/ts-server/share_file'
    save_path = os.path.expanduser('~/' + current_path)
    print('current_path:', current_path)
    print('save_path:', save_path)
    files = request.files.getlist('files')
    print('files:', files)

    for file in files:
        if '<' in file.filename or '>' in file.filename:
            return '文件名不能用<或>', 400
        if file.filename == '':
            # 文件名为空
            return '文件名为空', 400
        if file.filename == 'index.html':
            # 文件名危险
            return '不许用这个文件名', 400
        print('saved:', file.filename)
        file.save(os.path.join(save_path, file.filename))

    # 上传成功
    page = """
    <script>
    location.href = '/shared';
    </script>
    """
    return page, 200


@app.route('/share-file/get', methods=['POST'])
def shared_file_get():
    files = os.listdir('/Users/luojingfeng/html-project/ts-server/share_file/')
    return '@@|@@|@@'.join(files)


# noinspection bad-argument-type
@app.route('/share-file/get-file/<path:path>')
def share_file_get_file(path):
    basename = os.path.basename(path)
    return send_file(os.path.join('/Users/luojingfeng/html-project/ts-server/share_file/', basename), as_attachment=True)


@app.route('/love-eyes-exercise')
def love_eyes_exercise():
    return send_from_directory('.', 'love-eyes-exercise.html')


@app.route('/love-eyes.mp4.download')
def love_eyes_download():
    return send_file('./static/video/love-eyes-download.mp4', as_attachment=True, download_name='爱眼体操.mp4')


@app.route('/static/img/<path:path>')
def static_file(path):
    return send_file(os.path.join('./static/img/', path))


@app.route('/games/snake')
def snake_game():
    return send_from_directory('.', 'games/snake.html')


@app.route('/games/dazhuankuai')
def dazhaunkuai_game():
    return send_from_directory('.', 'games/dazhaunkuai.html')


@app.route('/games/2048')
def game_2048():
    return send_from_directory('.', 'games/2048.html')


@app.route('/shenfen_id_test')
def shenfen_id_test():
    return send_from_directory('.', 'shenfen_id_test.html')


@app.route('/ghost-search/<path:path>')
def ghost_search(path):
    page = """
    <h1>GHOST SEARCH</h1>
    <h2>No Answer!</h2>
    <hr>
    <p>You enter text is ghost knowed!</p>
    <p>HAHAHAHA</p>
    """
    print('GHOST SEARCH: search word=', path)
    return page, 666


@app.route('/fuck-box')
def fuck_box():
    return send_from_directory('.', 'fuck-box/index.html')


@app.route('/fuck-box-submit', methods=['POST'])
def fuck_box_submit():
    problem_type = request.form.get('type')
    msg = request.form.get('msg', '').strip()
    if msg == '':
        page = """
        <h1>信息为空</h1>
        <a href="/"><h1>返回主页</h1></a>
        """
        return page, 400
    try:
        with open(f'/Users/luojingfeng/html-project/ts-server/fuck-box/{problem_type}-{time.time()}.txt', 'w') as f:
            f.write(f'type: {problem_type}\nmsg: {msg}\n')
    except Exception as e:
        print(type(e).__name__)
        print(e)
        print(format_exc())
        page = f"""
            <h1>后端发生错误, 请查看以下报错信息:</h1>
            <p>type: {type(e).__name__}</p>
            <p>msg: {e}</p>
            <p>堆栈:</p>
            <p>{format_exc()}</p>
            <p>请把以上信息复制, 然后报告给作者</p>
            <a href="/"><h1>返回主页</h1></a>
        """
        return page, 500
    page = """
    <h1>提交成功!</h1>
    <a href="/"><h1>返回主页</h1></a>
    """
    return page, 200


@app.route('/pojie_python_xingqiu')
def pojie_python_xingqiu():
    return send_from_directory('.', 'pojie_python_xingqiu.html')


@app.route('/browser')
def browser():
    return send_from_directory('.', 'browser.html')


@app.route('/no-click-page')
def no_click_page():
    return send_from_directory('.', 'no-click-page.html')


@app.route('/lianxi_me')
def lianxi_me():
    return send_from_directory('.', 'lianxi_me.html')

@app.route('/del-ban-ip', methods=['POST'])
def del_ban_ip():
    json = request.get_json()
    passcode = json['passcode']
    if passcode == 'Szbt2015':
        try:
            with open('/Users/luojingfeng/html-project/ts-server/ban_ip.txt', 'w') as f:
                f.write('')
        except Exception:
            print(format_exc())
            return 'ERROR', 500
    else:
        return '密钥错误', 403
    return 'OK', 200

@app.route('/restart-service', methods=['POST'])
def restart_service():
    print('restart service')
    json = request.get_json()
    passcode = json['passcode']
    if passcode == 'Szbt2015':
        try:
            ip = get_real_ip()
            print('%s要求重启' % ip)
            sys.exit()
        except Exception:
            print(format_exc())
            return 'ERROR', 500
    else:
        return '密钥错误', 403


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=22334, threaded=True)