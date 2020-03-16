#!/user/bin/env python
# _*_ coding:utf-8 _*_

from urllib.request import urlopen
from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
import pymysql
import shutil
import time
import json
import os


baseurl="https://news.sina.com.cn/"
news={}
xttime=datetime.datetime.now().strftime('%Y-%m-%d %H')#获取系统当前时间
min=datetime.datetime.now().strftime('%M')
x="该页面没有内容"

##爬取评论
def pinglun(url,sqlid):
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    #cursor.execute("create table if not EXISTS pl(id  CHAR(100),plname CHAR(100),pldate CHAR(100),plnr CHAR(250))")
    plnames=[]
    pldatas=[]
    pldzs=[]
    n=0
    drive=webdriver.Chrome()#用于打开浏览器
    drive.get(url)
    time.sleep(3)#等待页面加载
    js = "window.scrollTo(0, document.body.scrollHeight)"#自动将页面拉到最下面
    drive.execute_script(js)
        #cursor.execute("INSERT INTO pl(plid,plname,pldate,pldz,plnr) value('" + sqlid + "','"+plnames[n-1]+"','" + pldatas[n - 1] + "','" + pldzs[n - 1] + "','" + p.text + "')")
    try:
        plnum = drive.find_element_by_css_selector("a[data-sudaclick='comment_sum_p']").text
        plurl = drive.find_element_by_css_selector("a[data-sudaclick='comment_sum_p']").get_attribute('href')
        if '0' in plnum:
            p = "该新闻没有评论"
            sql = """INSERT INTO pl(plid,plnr) value('%s','%s')"""%(sqlid,p)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            drive.close()
            return 0
        drive.get(plurl)
        time.sleep(3)
        js = "window.scrollTo(0, document.body.scrollHeight)"  # 自动将页面拉到最下面
        drive.execute_script(js)
        names = drive.find_element_by_css_selector("div[comment-type='latestWrap']").find_elements_by_css_selector("a[data-sudaclick='comment_usernickname_p']")
        pls = drive.find_element_by_css_selector("div[comment-type='latestWrap']").find_elements_by_css_selector("div[comment-type='itemTxt']")
        datas = drive.find_element_by_css_selector("div[comment-type='latestWrap']").find_elements_by_css_selector("span[class='time']")
        dznum = drive.find_element_by_css_selector("div[comment-type='latestWrap']").find_elements_by_css_selector("em[comment-type='voteNum']")
        for dz in dznum:
            if not dz.text:
                pldzs.append("0")
                continue
            pldzs.append(dz.text)
        for name in names:
            plnames.append(name.text)
        for data in datas:
            pldatas.append(data.text)
        for p in pls:
            n += 1
            plsqlid = sqlid + "-" + (str)(n)
            if not p.text:
                continue
            cursor.execute("INSERT INTO pl(plid,plname,pldate,pldz,plnr) value('" + sqlid + "','" + plnames[n - 1] + "','" + pldatas[n - 1] + "','" + pldzs[n - 1] + "','" + p.text + "')")
            db.commit()
        cursor.close()
        db.close()
        drive.close()
        return 0
    except:
        p = "该新闻没有评论"
        cursor.execute("INSERT INTO pl(plid,plnr) value('" + sqlid + "','" + p + "')")
        db.commit()
        cursor.close()
        db.close()
        drive.close()
        return 0

##链接数据库
def dbconnect():
    db=pymysql.connect("localhost","root","973249","news")
    cursor=db.cursor()##使用cursor方法创建一个光标对象
    cursor.execute("drop table if exists pl")
    cursor.execute("drop table if exists new")
    cursor.execute("create table new(id  VARCHAR(100) PRIMARY KEY,newtype CHAR(250),newtitle CHAR(250),newdate CHAR(100),newnr VARCHAR(10000))")
    cursor.execute("create table pl(id INT AUTO_INCREMENT PRIMARY KEY,plid  VARCHAR(100) ,plname CHAR(100),pldate CHAR(100),pldz CHAR(100),plnr CHAR(250),FOREIGN KEY (plid) REFERENCES new(id))")
    cursor.close()
    db.close()

##创建文件夹
def  creatdir():
    try:
        shutil.rmtree(r'd:/bise/时间' + xttime + '点' + min + '分/')  # 删除非空文件夹
    except FileNotFoundError:
        os.mkdir(r'd:/bise/时间' + xttime + '点' + min + '分/')  # 创建文件夹

##国内新闻
def guoneixinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url="d:/bise/时间" + xttime + "点"+ min +"分/国内新闻" + ".json"
    try:
        os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    titles=[]
    gnnews = {}
    gnurls = []
    n = 0
    div1 = bsObj.find("div", {"data-sudaclick": {"gn2_list_01"}})
    gnhrefs = div1.find_all("a")
    name=bsObj.find("div",{"id":{"blk_gntltop_01"}}).find("a",class_="titName ptn_26").get_text()
    gnnews.setdefault(name, {})
    for href in gnhrefs:
        titles.append(href.text)
        gnurls.append(href.get('href'))
    for gnurl in gnurls:
        gnessay = ""
        title=titles[n]
        n += 1
        sqlid="gn" + "-" + (str)(n)
        html = urlopen(gnurl)
        bsObj = BeautifulSoup(html, "html.parser")
        gnnews["国内新闻"].setdefault(n, {})
        gnnews["国内新闻"][n].setdefault("标题", title.strip())
        try:
            date = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps = bsObj.find("div", id="article").find_all("p")
        except AttributeError:
            date = "无"
            x="该页面无内容"
            gnnews["国内新闻"][n].setdefault("内容", x)
            sql="""insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')"""%(sqlid,'gn',title,date,x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps:
            gnessay = gnessay +"\t"+ p.text.strip()
        gnnews["国内新闻"][n].setdefault("时间", date)
        gnnews["国内新闻"][n].setdefault("内容", gnessay)
        sql="""insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')"""%(sqlid,'gn',title,date,gnessay)
        cursor.execute(sql)
        db.commit()
        pinglun(gnurl,sqlid)
    cursor.close()
    db.close()
    with open(save_url,'w') as f_obj:
        json.dump(gnnews,f_obj)

##国际新闻
def guojixinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url = "d:/bise/时间" + xttime + "点" + min + "分/国际新闻" + ".json"
    try:
        os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    titles=[]
    gjnews = {}
    gjurls = []
    m = 0
    div2 = bsObj.find("div", {"data-sudaclick": {"gj2_list_01"}})
    name=bsObj.find("div",{"id":{"blk_gjtltop_01"}}).find("a",{"class":{"titName ptn_27"}}).get_text()
    gjnews.setdefault(name, {})
    gjhrefs = div2.find_all("a")
    for href in gjhrefs:
        titles.append(href.text)
        gjurls.append(href.get('href'))
    for gjurl in gjurls:
        gjessay = ""
        title=titles[m]
        m += 1
        sqlid = "gj" + "-" + (str)(m)
        html = urlopen(gjurl)
        bsObj = BeautifulSoup(html, "html.parser")
        #gjnews.setdefault("国际新闻", {})
        gjnews["国际新闻"].setdefault(m, {})
        gjnews["国际新闻"][m].setdefault("标题", title.strip())
        try:
            date = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps = bsObj.find("div", id="article").find_all("p")
        except AttributeError:
            date = "无"
            x="该页面没有内容"
            gjnews["国际新闻"][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid,'gj' , title, date, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps:
            gjessay = gjessay +"\t"+ p.text.strip()
        gjnews["国际新闻"][m].setdefault("时间", date)
        gjnews["国际新闻"][m].setdefault("内容", gjessay)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid,'gj' , title, date, gjessay)
        cursor.execute(sql)
        db.commit()
        pinglun(gjurl, sqlid)
    cursor.close()
    db.close()
    with open(save_url,'w') as f_obj:
        json.dump(gjnews,f_obj)

##军事新闻
def junshixinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url = "d:/bise/时间" + xttime + "点" + min + "分/军事新闻" + ".json"
    try:
        os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    titles=[]
    jsnews = {}
    jsurls = []
    m = 0
    div = bsObj.find("div", {"data-sudaclick": {"mil2_list"}})
    jshrefs = div.find_all("a")
    name=bsObj.find("div",{"id":{"blk_jstltop_01"}}).find("a",{"class":{"titName ptn_28"}}).get_text()
    jsnews.setdefault(name, {})
    for href in jshrefs:
        titles.append(href.text)
        jsurls.append(href.get('href'))
    for jsurl in jsurls:
        jsessay = ""
        title=titles[m]
        m += 1
        sqlid="js" + "-" +(str)(m)
        html = urlopen(jsurl)
        bsObj = BeautifulSoup(html, "html.parser")
        #jsnews.setdefault("军事新闻", {})
        jsnews["军事新闻"].setdefault(m, {})
        jsnews["军事新闻"][m].setdefault("标题", title.strip())
        try:
            date = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps = bsObj.find("div", id="article").find_all("p")
        except AttributeError:
            date = "无"
            jsnews["军事新闻"][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid,'js' , title, date, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps:
            jsessay = jsessay + "\t" + p.text.strip()
        jsnews["军事新闻"][m].setdefault("时间", date)
        jsnews["军事新闻"][m].setdefault("内容", jsessay)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid,'js' , title, date, jsessay )
        cursor.execute(sql)
        db.commit()
        pinglun(jsurl, sqlid)
    cursor.close()
    db.close()
    with open(save_url,'w') as f_obj:
        json.dump(jsnews,f_obj)

#体育新闻
def tiyuxinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url = "d:/bise/时间" + xttime + "点" + min + "分/体育新闻" + ".json"
    try:
       os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    tynews={}
    #tynews.setdefault("体育新闻", {})
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    name_lq = bsObj.find("div", {"id": {"blk_tyxwlqup_01"}}).find("a").get_text()
    name_gjzt = bsObj.find("div", id="blk_tyxwgjztup_01").find("a").get_text()
    name_gnzt = bsObj.find("div",id="blk_tyxwgnztup_01").find("a").get_text()
    name_zhty = bsObj.find("div",id="blk_tyxwzhtyup_01").find("a").get_text()
    divs=bsObj.find("div",{"data-sudaclick":{"sports2_list"}})
    name_zhong=bsObj.find("div",{"id":{"blk_tytltop_01"}}).find("a",{"class":{"titName ptn_30"}}).get_text()
    tynews.setdefault(name_zhong, {})
    ##篮球新闻
    m=0
    titles=[]
    tynews["体育新闻"].setdefault(name_lq, {})
    divlq=divs.find("div",id="blk_tyxwlq_01")
    tyurls_lq=[]
    tyhrefs_lq=divlq.find_all("a")
    for tyhref_lq in tyhrefs_lq:
        titles.append(tyhref_lq.text)
        tyurls_lq.append(tyhref_lq.get('href'))
    for tyurl_lq in tyurls_lq:
        tyessay_lq = ""
        title=titles[m]
        m += 1
        sqlid = "tylq" + "-" + (str)(m)
        html=urlopen(tyurl_lq)
        bsObj=BeautifulSoup(html,"html.parser")
        #tynews["体育新闻"].setdefault("篮球",{})
        tynews["体育新闻"][name_lq].setdefault(m,{})
        tynews["体育新闻"][name_lq][m].setdefault("标题",title.strip())
        try:
            date_lq = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_lq = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_lq = "无"
            tynews["体育新闻"][name_lq][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid,'tylq' , title, date_lq, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_lq:
            tyessay_lq = tyessay_lq + "\t" + p.text.strip()
        tynews["体育新闻"][name_lq][m].setdefault("时间",date_lq)
        tynews["体育新闻"][name_lq][m].setdefault("内容", tyessay_lq)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid,'tylq' , title, date_lq, tyessay_lq)
        cursor.execute(sql)
        db.commit()
        pinglun(tyurl_lq, sqlid)
    ##国际足坛
    m = 0
    titles=[]
    tynews["体育新闻"].setdefault(name_gjzt, {})
    divgjzt=divs.find("div",id="blk_tyxwgjzt_01")
    tyurls_gjzt=[]
    tyhrefs_gjzt=divgjzt.find_all("a")
    for href in tyhrefs_gjzt:
        titles.append(href.text)
        tyurls_gjzt.append(href.get('href'))
    for tyurl_gjzt in tyurls_gjzt:
        tyessay_gjzt = ""
        title=titles[m]
        m += 1
        sqlid = "tygjzt" + "-" + (str)(m)
        html=urlopen(tyurl_gjzt)
        bsObj=BeautifulSoup(html,"html.parser")
        tynews["体育新闻"][name_gjzt].setdefault(m,{})
        tynews["体育新闻"][name_gjzt][m].setdefault("标题",title.strip())
        try:
            date_gjzt = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_gjzt = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_gjzt = "无"
            tynews["体育新闻"][name_gjzt][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'tygjzt', title, date_gjzt, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_gjzt:
            tyessay_gjzt = tyessay_gjzt + "\t" + p.text.strip()
        tynews["体育新闻"][name_gjzt][m].setdefault("时间",date_gjzt)
        tynews["体育新闻"][name_gjzt][m].setdefault("内容", tyessay_gjzt)
        try:
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'tygjzt', title, date_gjzt, tyessay_gjzt)
            cursor.execute(sql)
            db.commit()
            pinglun(tyurl_gjzt, sqlid)
        except pymysql.err.ProgrammingError:
            continue
    ##国内足坛
    m = 0
    titles=[]
    divgnzt=divs.find("div",id="blk_tyxwgnzt_01")
    tyurls_gnzt=[]
    tyhrefs_gnzt=divgnzt.find_all("a")
    for href in tyhrefs_gnzt:
        titles.append(href.text)
        tyurls_gnzt.append(href.get('href'))
    for tyurl_gnzt in tyurls_gnzt:
        tyessay_gnzt = ""
        title=titles[m]
        m += 1
        sqlid = "tygnzt" + "-" + (str)(m)
        html=urlopen(tyurl_gnzt)
        bsObj=BeautifulSoup(html,"html.parser")
        tynews["体育新闻"].setdefault(name_gnzt,{})
        tynews["体育新闻"][name_gnzt].setdefault(m,{})
        tynews["体育新闻"][name_gnzt][m].setdefault("标题",title.strip())
        try:
            date_gnzt = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_gnzt = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_gnzt = "无"
            tynews["体育新闻"][name_gnzt][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'tygnzt', title, date_gnzt, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_gnzt:
            tyessay_gnzt = tyessay_gnzt + "\t" + p.text.strip()
        tynews["体育新闻"][name_gnzt][m].setdefault("时间", date_gnzt)
        tynews["体育新闻"][name_gnzt][m].setdefault("内容", tyessay_gnzt)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'tygnzt', title, date_gnzt, tyessay_gnzt)
        cursor.execute(sql)
        db.commit()
        pinglun(tyurl_gnzt, sqlid)
    #综合体育
    m = 0
    titles=[]
    divzhty=divs.find("div",id="blk_tyxwzhty_01")
    tyurls_zhty=[]
    tyhrefs_zhty=divzhty.find_all("a")
    for href in tyhrefs_zhty:
        titles.append(href.text)
        tyurls_zhty.append(href.get('href'))
    for tyurl_zhty in tyurls_zhty:
        tyessay_zhty = ""
        title=titles[m]
        m += 1
        sqlid = "tyzhty" + "-" + (str)(m)
        html=urlopen(tyurl_zhty)
        bsObj=BeautifulSoup(html,"html.parser")
        tynews["体育新闻"].setdefault(name_zhty,{})
        tynews["体育新闻"][name_zhty].setdefault(m,{})
        tynews["体育新闻"][name_zhty][m].setdefault("标题",title.strip())
        try:
            date_zhty = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_zhty = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_zhty = "无"
            tynews["体育新闻"][name_zhty][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'tyzhty', title, date_zhty, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_zhty:
            tyessay_zhty = tyessay_zhty + p.text.strip()
        tynews["体育新闻"][name_zhty][m].setdefault("内容", tyessay_zhty)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'tyzhty', title, date_zhty, tyessay_zhty)
        cursor.execute(sql)
        db.commit()
        pinglun(tyurl_zhty, sqlid)
    cursor.close()
    db.close()
    with open(save_url,'w') as f_obj:
        json.dump(tynews,f_obj)

#财经新闻
def caijingxinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url = "d:/bise/时间" + xttime + "点" + min + "分/财经新闻" + ".json"
    try:
        os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    cjnews = {}
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    name_zh=bsObj.find("div",id="blk_cjtltop_01").find("a",class_="titName ptn_31").get_text()
    name_gngjcj=bsObj.find("div",id="blk_cjxwgngjcjup_01").find("div",class_="t_name").get_text()
    name_gp=bsObj.find("div",id="blk_cjxwgpggmgup_01").find("div",class_="t_name").get_text()
    name_lc=bsObj.find("div",id="blk_cjxwlcshup_01").find("div",class_="t_name").get_text()
    cjnews.setdefault(name_zh,{})
    cjnews[name_zh].setdefault(name_gngjcj,{})
    cjnews[name_zh].setdefault(name_gp, {})
    cjnews[name_zh].setdefault(name_lc, {})
    divs = bsObj.find("div", {"data-sudaclick": {"fin2_list"}})
    ##国内外财经
    m=0
    titles=[]
    cjurls_gngjcj=[]
    div_gngjcj=divs.find("div",id="blk_cjxwgngjcj_01")
    cjhrefs_gngjcj=div_gngjcj.find_all("a")
    for href in cjhrefs_gngjcj:
        titles.append(href.text)
        cjurls_gngjcj.append(href.get('href'))
    for cjurl_gngjcj in cjurls_gngjcj:
        essay_gngjcj = ""
        title=titles[m]
        m += 1
        sqlid = "cjgngjcj" + "-" + (str)(m)
        html=urlopen(cjurl_gngjcj)
        bsObj=BeautifulSoup(html,"html.parser")
        cjnews[name_zh][name_gngjcj].setdefault(m,{})
        cjnews[name_zh][name_gngjcj][m].setdefault("标题",title.strip())
        try:
            date_gngjcj = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_gngjcj = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_gngjcj = "无"
            cjnews[name_zh][name_gngjcj][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'cjgngjcj', title, date_gngjcj, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_gngjcj:
            essay_gngjcj = essay_gngjcj + "\t" + p.text.strip()
        cjnews[name_zh][name_gngjcj][m].setdefault("时间", date_gngjcj)
        cjnews[name_zh][name_gngjcj][m].setdefault("内容",essay_gngjcj)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'cjgngjcj', title, date_gngjcj, essay_gngjcj)
        cursor.execute(sql)
        db.commit()
        pinglun(cjurl_gngjcj, sqlid)
    ##股票
    m = 0
    titles=[]
    cjurls_gp = []
    div_gp = divs.find("div", id="blk_cjxwgpggmg_01")
    cjhrefs_gp = div_gp.find_all("a")
    for href in cjhrefs_gp:
        titles.append(href.text)
        cjurls_gp.append(href.get('href'))
    for cjurl_gp in cjurls_gp:
        essay_gp = ""
        title=titles[m]
        m += 1
        sqlid = "cjgp" + "-" + (str)(m)
        html = urlopen(cjurl_gp)
        bsObj = BeautifulSoup(html, "html.parser")
        cjnews[name_zh][name_gp].setdefault(m, {})
        cjnews[name_zh][name_gp][m].setdefault("标题", title.strip())
        try:
            date_gp = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_gp = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_gp = "无"
            cjnews[name_zh][name_gp][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'cjgp', title, date_gp, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_gp:
            essay_gp = essay_gp + "\t" + p.text.strip()
        cjnews[name_zh][name_gp][m].setdefault("时间", date_gp)
        cjnews[name_zh][name_gp][m].setdefault("内容", essay_gp)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'cjgp', title, date_gp, essay_gp)
        cursor.execute(sql)
        db.commit()
        pinglun(cjurl_gp, sqlid)
    ##理财
    m = 0
    titles=[]
    cjurls_lc = []
    div_lc = divs.find("div", id="blk_cjxwlcsh_01")
    cjhrefs_lc = div_lc.find_all("a")
    for href in cjhrefs_lc:
        titles.append(href.text)
        cjurls_lc.append(href.get('href'))
    for cjurl_lc in cjurls_lc:
        essay_lc = ""
        title=titles[m]
        m += 1
        sqlid = "cjlc" + "-" + (str)(m)
        html = urlopen(cjurl_lc)
        bsObj = BeautifulSoup(html, "html.parser")
        cjnews[name_zh][name_lc].setdefault(m, {})
        cjnews[name_zh][name_lc][m].setdefault("标题", title.strip())
        try:
            date_lc = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_lc = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_lc = "无"
            cjnews[name_zh][name_lc][m].setdefault("内容", x)
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s'.'%s','%s','%s','%s')""" % (sqlid, 'cjlc', title, date_lc, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_lc:
            essay_lc = essay_lc + "\t" + p.text.strip()
        cjnews[name_zh][name_lc][m].setdefault("时间", date_lc)
        cjnews[name_zh][name_lc][m].setdefault("内容", essay_lc)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'cjlc', title, date_lc, essay_lc)
        cursor.execute(sql)
        db.commit()
        pinglun(cjurl_lc, sqlid)
    cursor.close()
    db.close()
    with open(save_url,'w') as f_obj:
        json.dump(cjnews,f_obj)

##科技新闻
def kejixinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url = "d:/bise/时间" + xttime + "点" + min + "分/科技新闻" + ".json"
    try:
        os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    kjnews={}
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    name_zh=bsObj.find("div",id="blk_kjtltop_01").find("a",class_="titName ptn_36").get_text()
    name_hlw=bsObj.find("div",id="blk_kjxwhlwup_01").find("div",class_="t_name").get_text()
    name_kjts=bsObj.find("div",id="blk_kjxwkjtsup_01").find("div",class_="t_name").get_text()
    kjnews.setdefault(name_zh, {})
    kjnews[name_zh].setdefault(name_hlw,{})
    kjnews[name_zh].setdefault(name_kjts, {})
    divs = bsObj.find("div", {"data-sudaclick": {"tech2_list"}})
    ##互联网
    m=0
    titles=[]
    kjurls_hlw=[]
    div_hlw=divs.find("div",id="blk_kjxwhlw_01")
    kjhrefs_hlw=div_hlw.find_all("a")
    for href in kjhrefs_hlw:
        titles.append(href.text)
        kjurls_hlw.append(href.get('href'))
    for url_hlw in kjurls_hlw:
        title=titles[m]
        m+=1
        sqlid = "kjhlw" + "-" + (str)(m)
        essay_hlw=""
        html=urlopen(url_hlw)
        bsObj=BeautifulSoup(html,"html.parser")
        kjnews[name_zh][name_hlw].setdefault(m,{})
        kjnews[name_zh][name_hlw][m].setdefault("标题",title.strip())
        try:
            date_hlw = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_hlw = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_hlw = "无"
            kjnews[name_zh][name_hlw][m].setdefault("内容", "该页面没有内容")
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'kjhlw', title, date_hlw, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_hlw:
            essay_hlw=essay_hlw+"\t"+p.text.strip()
        kjnews[name_zh][name_hlw][m].setdefault("时间", date_hlw)
        kjnews[name_zh][name_hlw][m].setdefault("内容", essay_hlw)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'kjhlw', title, date_hlw,essay_hlw)
        cursor.execute(sql)
        db.commit()
        pinglun(url_hlw, sqlid)
    ##科技探索
    m = 0
    titles=[]
    kjurls_kjts = []
    div_kjts = divs.find("div", id="blk_kjxwkjts_01")
    kjhrefs_kjts = div_kjts.find_all("a")
    for href in kjhrefs_kjts:
        titles.append(href.text)
        kjurls_kjts.append(href.get('href'))
    for url_kjts in kjurls_kjts:
        title = titles[m]
        m += 1
        sqlid = "kjkjts" + "-" +(str)(m)
        essay_kjts = ""
        html = urlopen(url_kjts)
        bsObj = BeautifulSoup(html, "html.parser")
        kjnews[name_zh][name_kjts].setdefault(m, {})
        kjnews[name_zh][name_kjts][m].setdefault("标题", title.strip())
        try:
            date_kjts = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_kjts = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_kjts = "无"
            kjnews[name_zh][name_kjts][m].setdefault("内容", "该页面没有内容")
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'kjkjts', title, date_kjts, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_kjts:
            essay_kjts = essay_kjts + "\t" + p.text.strip()
        kjnews[name_zh][name_kjts][m].setdefault("时间", date_kjts)
        kjnews[name_zh][name_kjts][m].setdefault("内容", essay_kjts)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'kjkjts', title, date_kjts, essay_kjts)
        cursor.execute(sql)
        db.commit()
        pinglun(url_kjts, sqlid)
    cursor.close()
    db.close()
    with open(save_url,'w') as f_obj:
        json.dump(kjnews,f_obj)

 ##教育新闻
def jiaoyuxinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url = "d:/bise/时间" + xttime + "点" + min + "分/教育新闻" + ".json"
    #save_url = "d:/bise/时间2019-05-02 10点58分/娱乐新闻" + ".json"
    try:
        os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    jynews={}
    name=bsObj.find("div",id="blk_jytltop_01").find("a",class_="titName ptn_39").get_text()
    jynews.setdefault(name,{})
    jyurls=[]
    titles = []
    m=0
    div = bsObj.find("div", {"data-sudaclick": {"edu2_list"}})
    deljyhrefs=div.find_all("a",class_="videoNewsLeft")
    jyhrefs=div.find_all("a")
    for href in jyhrefs:
        if href in deljyhrefs:
            continue
        titles.append(href.text)
        jyurls.append(href.get('href'))
    del jyurls[0:2]
    del titles[0:2]
    for url in jyurls:
        if "blog" in url:
            continue
        title=titles[m]
        m+=1
        sqlid = "jy" + "-" +(str)(m)
        essay_jy=""
        html=urlopen(url)
        bsObj=BeautifulSoup(html,"html.parser")
        jynews[name].setdefault(m,{})
        jynews[name][m].setdefault("标题",title.strip())
        try:
            date = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps = bsObj.find("div", {"data-sudaclick": {"blk_content"}}).find_all("p")
        except AttributeError:
            date = "无"
            jynews[name][m].setdefault("内容", "该页面没有内容")
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'jy', title, date, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps:
            essay_jy=essay_jy+"\t"+p.text.strip()
        jynews[name][m].setdefault("时间", date)
        jynews[name][m].setdefault("内容",essay_jy)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'jy', title, date, essay_jy)
        cursor.execute(sql)
        db.commit()
        pinglun(url, sqlid)
    cursor.close()
    db.close()
    with open(save_url, 'w') as f_obj:
        json.dump(jynews, f_obj)

##娱乐新闻
def yulexinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url = "d:/bise/时间" + xttime + "点" + min + "分/娱乐新闻" + ".json"
    #save_url="d:/bise/时间2019-05-02 10点58分/娱乐新闻" + ".json"
    try:
        os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    ylnews = {}
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    name_zh=bsObj.find("div",id="blk_yltltop_01").find("a",class_="titName ptn_44").get_text()
    name_mxbg=bsObj.find("div",id="blk_ylxwmxbgup_01").find("div",class_="t_name").get_text()
    name_dyds=bsObj.find("div",id="blk_ylxwrmysup_01").find("div",class_="t_name").get_text()
    ylnews.setdefault(name_zh, {})
    ylnews[name_zh].setdefault(name_mxbg, {})
    ylnews[name_zh].setdefault(name_dyds, {})
    divs = bsObj.find("div", {"data-sudaclick": {"ent2_list"}})
    ##明星八卦
    m = 0
    titles = []
    div_mxbg = divs.find("div", id="blk_ylxwmxbg_01")
    ylurls_mxbg = []
    ylhrefs_mxbg = div_mxbg.find_all("a")
    for ylhref_mxbg in ylhrefs_mxbg:
         titles.append(ylhref_mxbg.text)
         ylurls_mxbg.append(ylhref_mxbg.get('href'))
    for ylurl_mxbg in ylurls_mxbg:
        if "slide" in ylurl_mxbg:
            continue
        ylessay_mxbg = ""
        title = titles[m]
        m += 1
        sqlid = "ylmxbg" + "-" + (str)(m)
        html = urlopen(ylurl_mxbg)
        bsObj = BeautifulSoup(html, "html.parser")
        ylnews[name_zh][name_mxbg].setdefault(m, {})
        ylnews[name_zh][name_mxbg][m].setdefault("标题", title.strip())
        try:
            date_mxbg = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_mxbg = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_mxbg = "无"
            ylnews[name_zh][name_mxbg][m].setdefault("内容", "该页面没有内容")
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'ylmxbg', title, date_mxbg, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_mxbg:
            ylessay_mxbg = ylessay_mxbg + "/t" + p.text.strip()
        ylnews[name_zh][name_mxbg][m].setdefault("时间", date_mxbg)
        ylnews[name_zh][name_mxbg][m].setdefault("内容", ylessay_mxbg)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'ylmxbg', title, date_mxbg, ylessay_mxbg)
        cursor.execute(sql)
        db.commit()
        pinglun(ylurl_mxbg, sqlid)
    ##电影电视
    m = 0
    titles = []
    div_dyds = divs.find("div", id="blk_ylxwrmys_01")
    ylurls_dyds = []
    ylhrefs_dyds = div_dyds.find_all("a")
    for ylhref_dyds in ylhrefs_dyds:
        titles.append(ylhref_dyds.text)
        ylurls_dyds.append(ylhref_dyds.get('href'))
    for ylurl_dyds in ylurls_dyds:
        if "slide" in ylurl_dyds:
            continue
        ylessay_dyds = ""
        title = titles[m]
        m += 1
        sqlid = "yldyds" + "-" + (str)(m)
        html = urlopen(ylurl_dyds)
        bsObj = BeautifulSoup(html, "html.parser")
        ylnews[name_zh][name_dyds].setdefault(m, {})
        ylnews[name_zh][name_dyds][m].setdefault("标题", title.strip())
        try:
            date_dyds = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps_dyds = bsObj.find("div", class_="article").find_all("p")
        except AttributeError:
            date_dyds = "无"
            ylnews[name_zh][name_dyds][m].setdefault("内容", "该页面没有内容")
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'yldyds', title, date_dyds, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps_dyds:
            ylessay_dyds = ylessay_dyds + "\t" + p.text.strip()
        ylnews[name_zh][name_dyds][m].setdefault("时间", date_dyds)
        ylnews[name_zh][name_dyds][m].setdefault("内容", ylessay_dyds)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'yldyds', title, date_dyds, ylessay_dyds)
        cursor.execute("insert into new(id,newtype,newtitle,newdate,newnr) values('" + sqlid + "','yldyds','" + title + "','" + date_dyds + "','" + ylessay_dyds + "')")
        db.commit()
        pinglun(ylurl_dyds, sqlid)
    cursor.close()
    db.close()
    with open(save_url, 'w') as f_obj:
        json.dump(ylnews, f_obj)

##世相
def shixiangxinwen():
    db = pymysql.connect("localhost", "root", "973249", "news")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    save_url = "d:/bise/时间" + xttime + "点" + min + "分/世相" + ".json"
    #save_url = "d:/bise/时间2019-05-02 10点58分/娱乐新闻" + ".json"
    try:
        os.remove(save_url)
    except FileNotFoundError:
        print("没有该文件")
    html = urlopen(baseurl)
    bsObj = BeautifulSoup(html, "html.parser")
    sxnews={}
    name=bsObj.find("div",id="blk_shtltop_01").find("a",class_="titName ptn_47").get_text()
    sxnews.setdefault(name,{})
    sxurls=[]
    titles = []
    m=0
    div = bsObj.find("div", {"data-sudaclick": {"sh2_list"}})
    sxhrefs=div.find_all("a")
    for href in sxhrefs:
        titles.append(href.text)
        sxurls.append(href.get('href'))
    for url in sxurls:
        title=titles[m]
        m+=1
        sqlid = "sx" + "-" + (str)(m)
        essay_sx=""
        html = urlopen(url)
        bsObj = BeautifulSoup(html, "html.parser")
        sxnews[name].setdefault(m, {})
        sxnews[name][m].setdefault("标题", title.strip())
        try:
            date = bsObj.find("div", {"class": {"date-source"}}).find("span", {"class": {"date"}}).get_text()
            ps = bsObj.find("div", id="article").find_all("p")
        except AttributeError:
            date = "无"
            sxnews[name][m].setdefault("内容", "该页面无内容")
            sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'sx', title, date, x)
            cursor.execute(sql)
            db.commit()
            cursor.close()
            db.close()
            continue
        for p in ps:
            essay_sx = essay_sx + "\t" + p.text.strip()
        sxnews[name][m].setdefault("时间", date)
        sxnews[name][m].setdefault("内容", essay_sx)
        sql = """insert into new(id,newtype,newtitle,newdate,newnr) values('%s','%s','%s','%s','%s')""" % (sqlid, 'sx', title, date, essay_sx)
        cursor.execute(sql)
        db.commit()
        pinglun(url, sqlid)
    cursor.close()
    db.close()
    with open(save_url, 'w') as f_obj:
        json.dump(sxnews, f_obj)

creatdir()
dbconnect()
guoneixinwen()
guojixinwen()
junshixinwen()
tiyuxinwen()
caijingxinwen()
kejixinwen()
jiaoyuxinwen()
yulexinwen()
shixiangxinwen()