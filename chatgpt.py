import os
import openai
from flask import Flask, request, render_template, redirect,stream_template,make_response,session
from flask_socketio import SocketIO,send, emit
CONNECTIONS = {}
class get_static:
    static_var = 1
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q7z\n\xec]/'
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
def get_completion(question):
    openai.api_key =session["token"]
    try:
        response = openai.Completion.create(model="text-davinci-003",
            prompt=f"{question}\n",
            temperature=0.9,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=None)
    except Exception as e:
        print(e)
        return e
    return response["choices"][0].text

@app.route('/login', methods=['GET', 'POST'])
def login():
    token = request.values.get("token")
    name = request.values.get("name")
    if not token:
        return 'NO'
    if name == 'almm':
        session["token"] = token
        session["username"] = name        
        socketio.emit('GetAiMsG',name + "连接成功！")
        return 'YES'
    else:
        session.pop('username', None)
        session.pop('token', None)
        socketio.emit('GetAiMsG',"登录失败，请输入正确的名字！")
        return 'NO'

@app.route('/')
def index():
    username = 'no'
    token = ''
    status='hello 请输入token 连接！'
    if 'username' in session:
        username = session["username"]
        token = session["token"]
        status='连接成功 欢迎光临'
    return  render_template("index.html",name=username,token=token,status=status)

@socketio.on("cts")
def message(msg):
#    print("message", msg)
    if 'username' in session:
        res = get_completion(msg)
        socketio.emit('GetAiMsG',res)
    else:
        socketio.emit('GetAiMsG', "hello 请输入token 连接！")

if __name__ == '__main__':
  socketio.run(app,host='0.0.0.0',port=80,debug='true')