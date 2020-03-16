#!/user/bin/env python
# _*_ coding:utf-8 _*_

from flask import Flask, render_template
import pymysql

app = Flask(__name__)  ##创建Flask应用程序实例，并传入_name__，作用是为了确定资源所在的路径


##定义路由及视图函数
# Flask中定义路由是通过装饰器实现的
# 路由默认只支持GET，如需添加，则需要自行添加
# @app.route('/',methods=['GET','POST'])
@app.route('/', methods={'GET', 'POST'})  # 这是一个装饰器
def index():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()
    def news(newlist,newtitle):
        sql = "SELECT count(*) FROM new WHERE newtype = '"+newtitle+"'"
        cursor.execute(sql)
        count = cursor.fetchone()
        for i in count:
            sum = i+1
        for x in range(1,sum):
            sql = "SELECT newtitle,id FROM new WHERE id = '"+newtitle+"-"+(str)(x)+"'"
            cursor.execute(sql)
            titile = cursor.fetchone()
            newlist.append(list(titile))
    cjnews=[]
    news(cjnews, 'cjgngjcj')
    news(cjnews, 'cjgp')
    news(cjnews, 'cjlc')
    '''for cjgngjcj in range(1,7):
        sql = "SELECT newtitle,id FROM new WHERE id = 'cjgngjcj-"+(str)(cjgngjcj)+"'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        cjnews.append(list(titile))
    for cjgp in range(1,8):
        sql = "SELECT newtitle,id FROM new WHERE id = 'cjgp-" + (str)(cjgp) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        cjnews.append(list(titile))
    for cjlc in range(1,5):
        sql = "SELECT newtitle,id FROM new WHERE id = 'cjlc-" + (str)(cjlc) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        cjnews.append(list(titile))'''
    gjnews=[]
    news(gjnews,'gj')
    '''for gj in range(1,21):
        sql = "SELECT newtitle,id FROM new WHERE id = 'gj-" + (str)(gj) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        gjnews.append(list(titile))'''
    gnnews = []
    news(gnnews,'gn')
    '''for gn in range(1, 26):
        sql = "SELECT newtitle,id FROM new WHERE id = 'gn-" + (str)(gn) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        gnnews.append(list(titile))'''
    jsnews=[]
    news(jsnews,'js')
    '''for js in range(1,11):
        sql = "SELECT newtitle,id FROM new WHERE id = 'js-" + (str)(js) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        jsnews.append(list(titile))'''
    jynews=[]
    news(jynews, 'jy')
    '''for jy in range(1,19):
        sql = "SELECT newtitle,id FROM new WHERE id = 'jy-" + (str)(jy) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        jynews.append(list(titile))'''
    kjnews=[]
    news(kjnews, 'kjhlw')
    news(kjnews, 'kjkjts')
    '''for kjhlw in range(1,8):
        sql = "SELECT newtitle,id FROM new WHERE id = 'kjhlw-" + (str)(kjhlw) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        kjnews.append(list(titile))
    for kjkjts in range(1,6):
        sql = "SELECT newtitle,id FROM new WHERE id = 'kjkjts-" + (str)(kjkjts) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        kjnews.append(list(titile))'''
    sxnews=[]
    news(sxnews,'sx')
    '''for sx in range(1,19):
        sql = "SELECT newtitle,id FROM new WHERE id = 'sx-" + (str)(sx) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        sxnews.append(list(titile))'''
    tynews=[]
    news(tynews, 'tylq')
    news(tynews, 'tygjzt')
    news(tynews, 'tygnzt')
    '''for tygnzt in range(1,6):
        sql = "SELECT newtitle,id FROM new WHERE id = 'tygnzt-" + (str)(tygnzt) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        tynews.append(list(titile))
    for tylq in range(1,6):
        sql = "SELECT newtitle,id FROM new WHERE id = 'tylq-" + (str)(tylq) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        tynews.append(list(titile))
    for tyzhty in range(1,4):
        sql = "SELECT newtitle,id FROM new WHERE id = 'tyzhty-" + (str)(tyzhty) + "'"
        cursor.execute(sql)
        titile = cursor.fetchone()
        tynews.append(list(titile))'''
    ylnews=[]
    news(ylnews, 'yldyds')
    news(ylnews, 'ylmxbg')
    cursor.close()
    db.close()
    return render_template('zhuye.html',cjnews=cjnews,gjnews=gjnews,
                           gnnews=gnnews,jsnews=jsnews,jynews=jynews,kjnews=kjnews,
                           sxnews=sxnews,tynews=tynews,ylnews=ylnews)
    #return render_template('zhuye.html', gnnews=gnnews)


# 使用同一个视图函数 来显示不同用户的内容
# <>定义路由参数，<>内需起一个名字,我们可以在<>中来限定参数的类型，如<int:order_id>则这个参数为int型
@app.route('/nr/<order_id>', methods={'GET', 'POST'})  # 这是一个装饰器
def h(order_id):
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()
    news = []
    nrsql = "SELECT newtitle,newdate,newnr FROM new WHERE id = '" + order_id + "'"
    cursor.execute(nrsql)
    new = cursor.fetchone()
    news = list(new)
    plsql = "SELECT plname,pldate,pldz,plnr FROM pl WHERE plid = '" + order_id + "'"
    cursor.execute(plsql)
    pls = []
    pl = cursor.fetchall()
    for i in list(pl):
        pls.append(list(i))
    cursor.close()
    db.close()
    return render_template("nr.html", news=news, pls=pls)


if __name__ == '__main__':
    # 执行app.run，就会将Flask程序运行在一个简易的服务器(这个服务器有由Flask提供，适用于测试的)
    app.run(debug=True)
