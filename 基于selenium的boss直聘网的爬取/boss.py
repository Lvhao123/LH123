# -*- coding: gb18030 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
import pymysql
import csv
import time

class BossSpider(object):
    driver_path = r"D:\chromedriver\chromedriver.exe"
    # option = webdriver.ChromeOptions()���������������������ʱ�Ĳ���
    # ��ͨ��option.add_experimental_option('excludeSwitches', ['enable-automation'])����Ϳ���ʹ���������Ϊ������ģʽ����ֹ��������վʶ�����ʹ����Selenium��
    # ��ʱ�Ϳ�����һ���̶��Ϲ�ܷ�����Ļ��ƣ�
    # �������д���ֻ��ʹ����google�����79�汾֮ǰ�İ汾
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
            #�������һҳ�еġ���һҳ����ť��֮ǰ�Ĳ�ͬ�����Ծ���try�������������˵���������һҳ����ʱ��������ѭ����
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
            # ����bsObj.find_all("div", class_='job-sec')�Ƿ��ص�һ���б���ʱ�б��˳��ᷢ���仯�Ӷ���˾���ֵĻ�ȡ�ͻ����
            # ���ԣ��Ҿ�����forѭ�������������е�bsObj.find_all("div", class_='job-sec')��
            # Ȼ������try����������������������ѭ�����ټ���ִ�У�����ҵ��ˣ���ֱ������ȫ����ѭ��
            try:
                company_name = div.find("div", class_="name").get_text()
                self.position.setdefault("��˾����", company_name)
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
        self.position.setdefault("ְλ", position_name)
        self.position.setdefault("нˮ", salary)
        self.position.setdefault("�ص�/��������/ѧ��", education)
        self.position.setdefault("ְλ����", desc)
        self.positions.append(self.position)
        self.save_sql()
        print(self.position)
        print("=" * 40)

    def save_csv(self):
        headers = ['��˾����', 'ְλ', 'нˮ', '�ص�/��������/ѧ��', 'ְλ����']
        with open('boss.csv', 'w', encoding='gb18030') as f:
            f_csv = csv.DictWriter(f, headers)
            f_csv.writeheader()
            f_csv.writerows(self.positions)

    def save_sql(self):
        db = pymysql.connect("localhost", "root", "973249", "boss")
        cursor = db.cursor()
        #sql = """INSERT INTO python(name,position,salary,education,describtion) VALUES('%s','%s','%s','%s','%s')"""%(self.position['��˾����'],self.position['ְλ'],self.position['нˮ'],self.position['�ص�/��������/ѧ��'],self.position['ְλ����'])
        cursor.execute('INSERT INTO python(name,position,salary,education,describtion) VALUES("%s","%s","%s","%s","%s")'%(self.position['��˾����'],self.position['ְλ'],self.position['нˮ'],self.position['�ص�/��������/ѧ��'],self.position['ְλ����']))
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
