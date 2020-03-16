#!/user/bin/env python
# _*_ coding:utf-8 _*_

from urllib.request import urlopen
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pymysql

def s():
    n = 0
    db = pymysql.connect("localhost", "root", "973249", "news", charset="utf8")
    cursor = db.cursor()  ##使用cursor方法创建一个光标对象
    cursor.execute(
        "create table if not EXISTS pl(id  CHAR(100),plname CHAR(100),pldate CHAR(100),pldz CHAR(100),plnr CHAR(250))")
    db.commit()
    pl = []
    sqlid = "n"
    plnames = []
    pldata = []
    pldzs = []
    drive = webdriver.Firefox()  # 用于打开浏览器
    drive.get("https://news.sina.com.cn/w/2019-04-25/doc-ihvhiewr8132316.shtml")
    time.sleep(3)  # 等待页面加载
    js = "window.scrollTo(0, document.body.scrollHeight)"  # 自动将页面拉到最下面
    drive.execute_script(js)
    try:
        plnum = drive.find_element_by_css_selector("a[data-sudaclick='comment_sum_p']").text
        plurl = drive.find_element_by_css_selector("a[data-sudaclick='comment_sum_p']").get_attribute('href')
        if '0' in plnum:
            p = "该新闻没有评论"
            cursor.execute("INSERT INTO pl(id,plnr) value('" + sqlid + "'" + ",'" + p + "')")
            db.commit()
            cursor.close()
            db.close()
            drive.close()
            return 0
        drive.get(plurl)
        time.sleep(3)
        js = "window.scrollTo(0, document.body.scrollHeight)"  # 自动将页面拉到最下面
        drive.execute_script(js)
        names = drive.find_element_by_css_selector("div[comment-type='latestWrap']").find_elements_by_css_selector(
            "a[data-sudaclick='comment_usernickname_p']")
        pls = drive.find_element_by_css_selector("div[comment-type='latestWrap']").find_elements_by_css_selector(
            "div[comment-type='itemTxt']")
        datas = drive.find_element_by_css_selector("div[comment-type='latestWrap']").find_elements_by_css_selector(
            "span[class='time']")
        dznum = drive.find_element_by_css_selector("div[comment-type='latestWrap']").find_elements_by_css_selector(
            "em[comment-type='voteNum']")
        for dz in dznum:
            if not dz.text:
                pldzs.append("0")
                continue
            pldzs.append(dz.text)
        for name in names:
            plnames.append(name.text)
        for data in datas:
            pldata.append(data.text)
        for p in pls:
            n += 1
            plsqlid = sqlid + (str)(n)
            if not p.text:
                continue
            cursor.execute(
                "INSERT INTO pl(id,plname,pldate,pldz,plnr) value('" + plsqlid + "','" + plnames[n - 1] + "','" +
                pldata[
                    n - 1] + "','" + pldzs[n - 1] + "','" + p.text + "')")
            db.commit()
        drive.close()
    except:
        p = "该新闻没有评论"
        cursor.execute("INSERT INTO pl(id,plnr) value('" + sqlid + "'" + ",'" + p + "')")
        db.commit()
        cursor.close()
        db.close()
        drive.close()
#m=bsObj.find_all("div",class_="item clearfix")
s()