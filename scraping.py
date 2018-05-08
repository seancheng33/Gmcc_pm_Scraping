'''
@Author : sean cheng
@Email  : aya234@163.com
@CreateTime   : 2018/5/3
'''
import configparser
import os
import re
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select

config = configparser.ConfigParser()
config.read_file(open('config.ini','r'))

driver = webdriver.Chrome(executable_path=os.path.abspath('./lib/chromedriver.exe'))
driver.set_window_size(1366, 768)
driver.get(config.get("basic","url"))

driver.find_element_by_xpath('//*[@id="name"]').send_keys(config.get("basic","username"))
driver.find_element_by_xpath('/html/body/div/div/div[2]/div/form/div[3]/input').send_keys(config.get("basic","password"))

#
sleep(10)
driver.find_element_by_xpath('/html/body/div/div/div[2]/div/form/div[5]/a').click()

driver.find_element_by_xpath('//*[@id="header"]/div[3]/div/div/ul/li[5]/a').click()
driver.find_element_by_xpath('//*[@id="submenus160"]/li[2]/a').click()

driver.implicitly_wait(10)  # 浏览器智能等待10秒
driver.switch_to.frame("framecontent")  # 要获取到页面中的iframe，如果不这个做，获取元素或报错
# 重新提交条件搜索出内容
company = Select(driver.find_element_by_xpath('//*[@id="subBranch"]'))
company.select_by_index(0)

# page_length = Select(driver.find_element_by_xpath('//*[@id="data-table_length"]/label/select'))
# page_length.select_by_visible_text('1000')

driver.find_element_by_xpath('//*[@id="submitSearch"]').click()

driver.implicitly_wait(10)

# page_num = driver.find_element_by_xpath('//*[@id="data-table_info"]')
# print(page_num.text)

url_all = []

trs = driver.find_elements_by_xpath('//*[@id="data-table"]/tbody/tr')
for tr in trs:
    tr_html = tr.get_attribute('innerHTML')
    soup = BeautifulSoup(tr_html,'html.parser')
    data_list = soup.find_all('td')
    url_list = data_list[-1].find_all('a')
    url = url_list[-1].get('href')

    url_fix =re.findall('"(.*)"', url)  # 通过正则表达式获取两个引号中的内容
    # 上面获取到的内容，是一个list，但实际只用一个值
    url_fix = config.get("basic", "base_url") + url_fix[0]   # 在前面加上基础的网址,组合成一段完整的网址

    print(data_list[0].text, url_fix)

    url_all.append(url_fix)
    # 获取全部的内容，分离组合里面的查看里面的url出来，然后就直接重新打开这个页面

for item_url in url_all:
    driver.get(item_url)

    order_id = driver.find_element_by_xpath('//*[@id="tbody_1"]/table/tbody/tr[1]/td[1]')

    d_trs = driver.find_elements_by_xpath('//*[@id="details-table"]/tbody/tr')
    print(order_id.text)
    for d_tr in d_trs:
        print(d_tr.text)


# driver.quit()