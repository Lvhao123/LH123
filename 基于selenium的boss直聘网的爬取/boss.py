# -*- coding: gb18030 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
import pymysql
import csv
import time

class BossSpider(object):
    driver_path = r"D:\chromedriver\chromedriver.exe"
    # option = webdriver.ChromeOptions()代码是设置浏览器在启动时的参数
    # 再通过option.add_experimental_option('excludeSwitches', ['enable-automation'])代码就可以使浏览器设置为开发者模式，防止被各大网站识别出来使用了Selenium，
    # 这时就可以在一定程度上规避反爬虫的机制，
    # 但这两行代码只能使用在google浏览器79版本之前的版本
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=BossSpider.driver_path, options=self.option)
        self.url = "https://www.zhipin.com/c101200100/?query=python&page=1&ka=page-1"
        self.start_url = "https://www.zhipin.com"
        self.positions = []
        self.position = {}

    def run(self):
        self.create_mysql()
        self.driver.get(self.url)
        while True:
            self.driver.execute_script("window.open()")
            source = self.driver.page_source
            self.page_list_url(source)
            self.driver.switch_to.window(self.driver.window_handles[0])
            #由于最后一页中的“下一页”按钮与之前的不同。所以就用try方法，当报错就说明到了最后一页，这时就跳出死循环。
            try:
                btn = self.driver.find_element_by_xpath("//a[@class='next']")
                self.driver.execute_script("arguments[0].click();", btn)
            except:
                break
            break
            # time.sleep(5)
        self.save_csv()
        self.driver.close()



    def page_list_url(self, source):
        bsObj = BeautifulSoup(source,'lxml')
        spans = bsObj.find_all('span',class_='job-name')
        for span in spans:
            url = span.find('a').get('href')
            page_url = self.start_url + url
            print(page_url)
            self.result_detail_page(page_url)
            time.sleep(5)
            break
        self.driver.close()


    def result_detail_page(self, url):
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(url)
        source = self.driver.page_source
        self.parse_page(source)


    def parse_page(self, source):

        bsObj = BeautifulSoup(source, 'lxml')
        div_company = bsObj.find_all("div", class_='job-sec')
        for div in div_company:
            # 由于bsObj.find_all("div", class_='job-sec')是返回的一个列表，有时列表的顺序会发生变化从而公司名字的获取就会出错，
            # 所以，我就用了for循环，来遍历所有的bsObj.find_all("div", class_='job-sec')，
            # 然后，再用try方法，如果报错就跳出本次循环，再继续执行，如果找到了，就直接跳出全部的循环
            try:
                company_name = div.find("div", class_="name").get_text()
                self.position.setdefault("公司名字", company_name)
                break
            except:
                continue
        #company_name = div_company[3].find("div",class_="name").get_text()
        div_position_name = bsObj.find_all("div", class_="info-primary")
        h1 = div_position_name[0].find("div", class_="name")
        position_name = h1.find('h1').get_text()
        salary = h1.find('span', class_='salary').get_text()
        education = div_position_name[0].find("p").get_text()
        print(type(education))
        desc = div_company[0].find("div", class_="text").get_text()
        self.position.setdefault("职位", position_name)
        self.position.setdefault("薪水", salary)
        self.position.setdefault("地点/工作经验/学历", education)
        self.position.setdefault("职位描述", desc)
        self.positions.append(self.position)
        self.save_sql()
        print(self.position)
        print("=" * 40)

    def save_csv(self):
        headers = ['公司名字', '职位', '薪水', '地点/工作经验/学历', '职位描述']
        with open('boss.csv', 'w', encoding='gb18030') as f:
            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(self.positions)

    def save_sql(self):
        db = pymysql.connect("localhost", "root", "973249", "boss")
        cursor = db.cursor()
        #sql = """INSERT INTO python(name,position,salary,education,describtion) VALUES('%s','%s','%s','%s','%s')"""%(self.position['公司名字'],self.position['职位'],self.position['薪水'],self.position['地点/工作经验/学历'],self.position['职位描述'])
        cursor.execute('INSERT INTO python(name,position,salary,education,describtion) VALUES("%s","%s","%s","%s","%s")'%(self.position['公司名字'],self.position['职位'],self.position['薪水'],self.position['地点/工作经验/学历'],self.position['职位描述']))
        cursor.close()
        db.commit()
        db.close()



    def create_mysql(self):
        db = pymysql.connect("localhost", "root", "973249", "boss")
        cursor = db.cursor()
        cursor.execute("drop table if exists python")
        cursor.execute("create table python("
                       "name VARCHAR(1000),"
                       "position VARCHAR(1000),"
                       "salary VARCHAR(1000),"
                       "education VARCHAR(1000),"
                       "describtion VARCHAR(5000)"
                       ")")
        cursor.close()
        db.close()




if __name__ == '__main__':
    boss = BossSpider()
    boss.run()
