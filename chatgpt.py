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
    users={}
    tempm={}
    @gen.coroutine
    def open(self):
        print("WebSocket open")
        token = self.get_secure_cookie("token")
        name = self.get_secure_cookie("name")
        msg = 'hello 请输入token 连接！'
        if token and token != 'None':
             msg = '已经连接成功 欢迎光临'
             self.users[name]=self
        res = {'data':msg,'t':0}
        res = json.dumps(res) 
        self.write_message(res)

    @gen.coroutine
    def on_message(self, jsonstr):
        token = self.get_secure_cookie('token')
        name = self.get_secure_cookie('name')
        tk = json.loads(jsonstr)
        #token = tk["tk"]
        message = tk["msg"]
        ctype = tk["type"]
        if token and token != 'None':
             openai.api_key = token
             res = ''
             if ctype == 0:
                res = yield self.get_question(message)
                res = json.dumps({'data':res,'t':0}) 
             if ctype == 1:
                res = yield self.get_question_images(message)
             if self.users.get(name) is not None:
                self.users[name].write_message(res)
                if self.tempm.get(name) is not None:
                   self.users[name].write_message(self.tempm[name])
                   del self.tempm[name]
             else:
                self.tempm[name]=res

    def on_close(self):
        print("WebSocket closed")
        name = self.get_secure_cookie("name")
        if self.users.get(name) is not None:
           del self.users[name]
    async def get_question(self, question):
        try:
          response = await  openai.Completion.acreate(
            model="gpt-3.5-turbo",
            prompt=f"{question}\n",
#            prompt=f"<|endoftext|>{question}\n--\nLabel:",
#            model= "content-filter-alpha",
            temperature=0.9,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.5,
            stop=None)
        except Exception as e:
#          print(e)
          return str(e)
        return response["choices"][0].text
#        await gen.sleep(6)
#        return q+'---NO'
    async def get_question_images(self, question):
        try:
          response = openai.Image.create(prompt=question,
            n=1,
            response_format='b64_json',
            size="1024x1024")
        except Exception as e:
          return  json.dumps({'data':str(e),'t':0})
        return json.dumps({'data':response['data'][0]['b64_json'],'t':1})
#
esults = [{
      "categories": {
        "hate": False,
        "hate/threatening": False,
        "self-harm": False,
        "sexual": True,
        "sexual/minors": True,
        "violence": False,
        "violence/graphic": False
      },
      "category_scores": {
        "hate": 0.18805529177188873,
        "hate/threatening": 0.0001250059431185946,
        "self-harm": 0.0003706029092427343,
        "sexual": 0.0008735615410842001,
        "sexual/minors": 0.0007470346172340214,
        "violence": 0.0041268812492489815,
        "violence/graphic": 0.00023186142789199948
      },
      "flagged": False
    }]
def make_app():
    settings = {
      "websocket_ping_interval":None,#链接关闭问题
      "websocket_ping_timeout":60,
      "template_path":os.path.join(os.path.dirname(__file__), "templates"),
      "static_path": os.path.join(os.path.dirname(__file__), "static"),
      "login_url": "/login",
      "xsrf_cookies": True,
      "cookie_secret":"2hcicVu+TqShDpfsjMWQLZ0Mkq5NPEWSk9fi0zsSt0A=",
      "debug":True
     }   
    return tornado.web.Application([(r"/", MainHandler),(r"/login", LoginHandler),(r"/cts", ChatSocketHandler)],**settings)
#ssl._create_default_https_context = ssl._create_unverified_context 好像没有什么卵用
async def main():
    app = make_app()
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(os.path.join(os.path.abspath("."), "certificate.pem"),os.path.join(os.path.abspath("."), "key.pem"))
    http_server = tornado.httpserver.HTTPServer(app,ssl_options=ssl_ctx)
    http_server.listen(443)   

    await asyncio.Event().wait()
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    asyncio.run(main())

