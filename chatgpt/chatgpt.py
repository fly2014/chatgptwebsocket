import os
import openai
from flask import Flask, request, render_template, redirect,stream_template,make_response,session
from flask_socketio import SocketIO,send, emit
CONNECTIONS = {}

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q7z\n\xec]/'
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    token=request.values.get("token")
    name=request.values.get("name")
    if not token:
        return 'NO';
    if name == 'almm':
        session["token"]=token
        session["username"]=name
        socketio.emit('GetAiMsG',name+ "连接成功！")
        return 'YES'
    else:
        session.pop('username', None)
        session.pop('token', None)
        socketio.emit('GetAiMsG',name+ "连接失败！")
        return 'NO'

@app.route('/')
def index():
    username='no'
    if 'username' in session:
        username=session["username"]
    return  render_template("index.html",name=username)

@socketio.on("cts")
def message(msg):
    print("message", msg)
    if 'username' in session:
        socketio.emit('GetAiMsG',msg+'听不懂')
    else:
        socketio.emit('GetAiMsG', "hello 请输入token 连接！")

if __name__ == '__main__':
  socketio.run(app,host='0.0.0.0',port=80,debug='true')