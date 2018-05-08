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

page_length = Select(driver.find_element_by_xpath('//*[@id="data-table_length"]/label/select'))
page_length.select_by_visible_text('50')

driver.find_element_by_xpath('//*[@id="submitSearch"]').click()

driver.implicitly_wait(10)

# page_num = driver.find_element_by_xpath('//*[@id="data-table_info"]')
# print(page_num.text)

url_all = []
order_list = []

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

    # print(data_list[0].text, url_fix)
    order_dict = {}
    order_dict['orderId'] = data_list[0].text
    order_dict['stationId'] = data_list[1].text
    order_dict['stationName'] = data_list[2].text
    order_dict['sended'] = data_list[8].text
    order_dict['submitTime'] = data_list[9].text
    order_dict['status'] = data_list[10].text
    # order_dict['examine'] = data_list[12].text
    order_dict['company'] = data_list[11].text
    # order_dict['processing'] = []

    order_list.append(order_dict)

    url_all.append(url_fix)
    # 获取全部的内容，分离组合里面的查看里面的url出来，然后就直接重新打开这个页面


for item_url in url_all:
    driver.get(item_url)  # 直接使用上面的分离出来的url打开为新页面，处理步骤的分页功能失效，直接加载了全部的步骤出来，方便了不用判断步骤的分页

    order_id = driver.find_element_by_xpath('//*[@id="tbody_1"]/table/tbody/tr[1]/td[1]').text  # 详单里面的ID，
    d_trs = driver.find_elements_by_xpath('//*[@id="details-table"]/tbody/tr')
    processing_list = []  # 保存全部的处理进程
    # print(order_id.text)
    for d_tr in d_trs:
        txt = d_tr.text
        processing_list.append(txt.split(' '))
    examine_num = 0
    reject_list = []
    for i in processing_list:
        if i[0] == '省公司稽核组审核':
            examine_num += 1
            examine_dict = {}
            examine_dict['num'] = examine_num
            examine_dict['name'] = i[1]
            try:
                examine_dict['time'] = i[3]
            except IndexError:
                examine_dict['time'] = '未处理'
            try:
                examine_dict['status'] = i[2]
            except IndexError:
                examine_dict['status'] = '未处理'
            reject_list.append(examine_dict)

    for item in order_list:
        if item['orderId'] == order_id:
            item['rejectNum'] = examine_num - 1  # 如果只有一次，就是没有退回，如果两次，就是有一次退回，以此类推。
            item['processing'] = processing_list
            item['rejectList'] = reject_list

print(order_list)

driver.quit()