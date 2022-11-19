from flask import Flask, request  # 为什么tornado用不了?
from argparse import ArgumentParser
from fetch import fetch, QuestionNotFound  # 查答案
from json import dumps  # 打包
from random import choice  # 小彩蛋

app = Flask(__name__)

apser = ArgumentParser(description="题库api服务器", epilog="试试能不能直接用在ocs网课助手上")
apser.add_argument("port", help="在指定端口上运行", default=8000, type=int, nargs='?')
args = apser.parse_args()
port = args.port


@app.route('/')
def get():
    query = request.args.get('question')
    if not query:
        res = {
            'code': 203,
            'msg': '请输入question参数,question参数必须非空!'
        }
        return dumps(res, ensure_ascii=0)
    try:
        question, answer = fetch(query)
        res = {
            'code': 200,
            'data': {
                "question": question,
                "answer": answer
            }
        }
        return dumps(res, ensure_ascii=0)
    except QuestionNotFound:
        expressions = "😢😭😅😥😫😓🙃🤕🥺🤮🤔"
        res = {
            'code': 203,
            'data': {
                "question": query,
                "answer": "查不到这道题%s" % choice(expressions)
            }
        }
        return dumps(res, ensure_ascii=0)


@app.errorhandler(404)
def fnfe(e):  # file not found error
    return '<p>ErrorInfo:%s</p><p>Redirecting...</p><script>window.location="/";</script>' % e
# handdle 404 err


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=1)
