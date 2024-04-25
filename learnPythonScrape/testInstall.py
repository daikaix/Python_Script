# from selenium import webdriver
# browser = webdriver.Chrome()

# from selenium import webdriver
# browser = webdriver.PhantomJS()
# browser.get('https://www.baidu.com')
# print(browser.current_url)

# from flask import Flask
# app = Flask(__name__)

# @app.route("/")
# def hello():
#     return "Hello World!"
# if __name__ == "__main__":
#     app.run()

import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([(r"/", MainHandler),])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()





"""
pip3 install pyquery

Clash - Windows => HTTP Specify Protocal | PAC  或者 退出代理模式 => 如果最新版都不支持 pyspider, 没有必要使用 pyspider

"""