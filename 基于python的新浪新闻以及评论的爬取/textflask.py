#!/user/bin/env python
# _*_ coding:utf-8 _*_

from flask import Flask,render_template

app = Flask(__name__)##创建Flask应用程序实例，并传入_name__，作用是为了确定资源所在的路径

##定义路由及视图函数
#Flask中定义路由是通过装饰器实现的
#路由默认只支持GET，如需添加，则需要自行添加
#@app.route('/',methods=['GET','POST'])
@app.route('/')#这是一个装饰器
def hello_world():
     return render_template("text.html")

#使用同一个视图函数 来显示不同用户的内容
#<>定义路由参数，<>内需起一个名字,我们可以在<>中来限定参数的类型，如<int:order_id>则这个参数为int型
@app.route('/order/<order_id>')#这是一个装饰器
def h(order_id):
    #参数类型默认为字符串,unicode
    #需要在视图函数()内填入参数名，那么后面的代码才能去使用
     return render_template("text.html")

if __name__ == '__main__':
#执行app.run，就会将Flask程序运行在一个简易的服务器(这个服务器有由Flask提供，适用于测试的)
    app.run(debug=True)