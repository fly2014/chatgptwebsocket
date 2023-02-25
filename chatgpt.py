import os
import openai
import json
import ssl
import asyncio
from tornado import gen
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.options
import os.path
import markdown
import uuid
import threading 
from time import sleep
class MainHandler(tornado.web.RequestHandler):
   def get(self):
         name = self.get_secure_cookie('name')
         token = self.get_secure_cookie('token')
         status = 'hello 请输入token 连接！'
         inputtype = 'text'
         if token and token != 'None':
            status = '连接成功 欢迎光临'
            inputtype = 'password'
         self.render("index.html",name=name,token=token,status=status,inputtype=inputtype)

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("NO")
        self.clear_all_cookies()
    def post(self, *args, **kwargs):
         token = self.get_argument("token")
         name = self.get_argument("name")
         if not token:
           self.write('NO') 
         if name == 'almm':#默认验证名字才能使用 部署请修改 判断openapi
            self.set_secure_cookie("name", name,expires_days=None)
            self.set_secure_cookie("token",token)
            self.write('YES')
         else:
            self.clear_all_cookies()
            self.write('NO')

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    @gen.coroutine
    def open(self):
        print("WebSocket open")
        token = self.get_secure_cookie("token")
        name = self.get_secure_cookie("name")
        msg = 'hello 请输入token 连接！'
        if token and token != 'None':
             msg = '已经连接成功 欢迎光临'
        self.write_message(msg)

    @gen.coroutine
    def on_message(self, jsonstr):
        token = self.get_secure_cookie('token')
        tk = json.loads(jsonstr)
        token=tk["tk"]
        message=tk["msg"]
        if token and token != 'None':
             openai.api_key =token
             res = yield self.get_question(message)
             self.write_message(markdown.markdown(res))

    def on_close(self):
        print("WebSocket closed")

    async def get_question(self, question):
        try:
          response =await  openai.Completion.acreate(model="text-davinci-003",
            prompt=f"{question}\n",
            temperature=0.9,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=None)
        except Exception as e:
#          print(e)
          return e.error['message']
        return response["choices"][0].text
#        await gen.sleep(6)
#        return q+'---NO'

def make_app():
    settings = {
      "websocket_ping_interval":5,
      "template_path":os.path.join(os.path.dirname(__file__), "templates"),
      "static_path": os.path.join(os.path.dirname(__file__), "static"),
      "login_url": "/login",
      "xsrf_cookies": True,
      "cookie_secret":"2hcicVu+TqShDpfsjMWQLZ0Mkq5NPEWSk9fi0zsSt0A=",
      "debug":True
     }
    return tornado.web.Application([(r"/", MainHandler),(r"/login", LoginHandler),(r"/cts", ChatSocketHandler)],**settings)

async def main():
    app = make_app()
    app.listen(80)   
    await asyncio.Event().wait()
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    asyncio.run(main())

