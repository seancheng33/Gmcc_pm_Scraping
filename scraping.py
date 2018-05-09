'''
@Author : sean cheng
@Email  : aya234@163.com
@CreateTime   : 2018/5/3
'''
import configparser
import os
import re
import time

import xlsxwriter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select

config = configparser.ConfigParser()
config.read_file(open('config.ini', 'r'))

driver = webdriver.Chrome(executable_path=os.path.abspath('./lib/chromedriver.exe'))
driver.set_window_size(1366, 768)
driver.get(config.get("basic", "url"))

driver.find_element_by_xpath('//*[@id="name"]').send_keys(config.get("basic", "username"))
driver.find_element_by_xpath('/html/body/div/div/div[2]/div/form/div[3]/input').send_keys(
    config.get("basic", "password"))
driver.find_element_by_xpath('/html/body/div/div/div[2]/div/form/div[4]/input').send_keys('')
# 发送一个空值过去，让输入光标停留在输入校验码的框里面

#
time.sleep(10)
driver.find_element_by_xpath('/html/body/div/div/div[2]/div/form/div[5]/a').click()

driver.find_element_by_xpath('//*[@id="header"]/div[3]/div/div/ul/li[5]/a').click()
driver.find_element_by_xpath('//*[@id="submenus160"]/li[2]/a').click()

driver.implicitly_wait(10)  # 浏览器智能等待10秒
driver.switch_to.frame("framecontent")  # 要获取到页面中的iframe，如果不这个做，获取元素或报错
# 重新提交条件搜索出内容
company = Select(driver.find_element_by_xpath('//*[@id="subBranch"]'))
company.select_by_index(0)
send_order = Select(driver.find_element_by_xpath('//*[@id="isSend"]'))
send_order.select_by_index(0)

page_length = Select(driver.find_element_by_xpath('//*[@id="data-table_length"]/label/select'))
page_length.select_by_visible_text('1000')  # 显示1000条数据，基本上所有的数据都可以显示出来

driver.find_element_by_xpath('//*[@id="submitSearch"]').click()

driver.implicitly_wait(100)
# time.sleep(2) # 需要这样停数秒，才能获取到
# page_num = driver.find_element_by_id('data-table_info').text
# total_page = re.findall('共(.*)页',page_num)
# total_page = int(total_page[0].replace(' ',''))
# print(total_page[0].replace(' ',''))

url_all = []
order_list = []

trs = driver.find_elements_by_xpath('//*[@id="data-table"]/tbody/tr')
for tr in trs:
    tr_html = tr.get_attribute('innerHTML')
    soup = BeautifulSoup(tr_html, 'html.parser')
    data_list = soup.find_all('td')
    url_list = data_list[-1].find_all('a')
    url = url_list[-1].get('href')

    url_fix = re.findall('"(.*)"', url)  # 通过正则表达式获取两个引号中的内容
    # 上面获取到的内容，是一个list，但实际只用一个值
    url_fix = config.get("basic", "base_url") + url_fix[0]  # 在前面加上基础的网址,组合成一段完整的网址

    # print(data_list[0].text, url_fix)

    order_dict = {}

    order_dict['orderId'] = data_list[0].text
    order_dict['stationId'] = data_list[1].text
    order_dict['stationName'] = data_list[2].text
    order_dict['sended'] = data_list[8].text
    order_dict['submitTime'] = data_list[9].text
    order_dict['status'] = data_list[10].text
    # order_dict['operator'] = data_list[12].text
    order_dict['company'] = data_list[11].text
    # order_dict['processing'] = []

    order_list.append(order_dict)

    url_all.append(url_fix)
    #  获取全部的内容，分离组合里面的查看里面的url出来，然后就直接重新打开这个页面

    driver.find_element_by_xpath('//*[@id="data-table_paginate"]/a[3]').click()  # 点击下一页，继续获取内容

for item_url in url_all:
    driver.get(item_url)  # 直接使用上面的分离出来的url打开为新页面，处理步骤的分页功能失效，直接加载了全部的步骤出来，方便了不用判断步骤的分页

    order_id = driver.find_element_by_xpath('//*[@id="tbody_1"]/table/tbody/tr[1]/td[1]').text  # 详单里面的ID，
    d_trs = driver.find_elements_by_xpath('//*[@id="details-table"]/tbody/tr')
    processing_list = []  # 保存全部的处理进程
    # print(order_id.text)
    for d_tr in d_trs:
        tr_html = d_tr.get_attribute('innerHTML')
        soup = BeautifulSoup(tr_html, 'html.parser')
        data_list = soup.find_all('td')
        tmp_list = []
        for item in data_list:
            tmp_list.append(item.text)
        processing_list.append(tmp_list)
    examine_num = 0
    reject_list = []

    # 获取只包含‘省公司’的进程内容
    for i in processing_list:
        examine_dict = {}
        if '省公司' in i[0]:
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

    #  查找不同意的次数
    for item in reject_list:
        if '不同意' in item['status']:
            examine_num += 1

    for item in order_list:
        if item['orderId'] == order_id:
            item['current_operator'] = processing_list[-1][1]
            item['rejectNum'] = examine_num
            # item['processing'] = processing_list
            item['rejectList'] = reject_list

# print(order_list)

# 内容写入excle文件中
filename = time.strftime('%Y%m%d', time.localtime(time.time()))
workbook = xlsxwriter.Workbook('./data/' + filename + '.xlsx')
worksheet = workbook.add_worksheet(filename)

# 设置列宽,
worksheet.set_column('A:A', 15)
worksheet.set_column('B:B', 15)
worksheet.set_column('C:C', 25)
worksheet.set_column('D:D', 8)
worksheet.set_column('E:E', 10)
worksheet.set_column('F:F', 16)
worksheet.set_column('G:G', 10)
worksheet.set_column('H:H', 5)
worksheet.set_column('I:I', 30)
worksheet.set_column('J:J', 10)
worksheet.set_column('K:K', 30)
worksheet.set_column('L:L', 10)
worksheet.set_column('M:M', 30)
worksheet.set_column('N:N', 10)
worksheet.set_column('O:O', 30)
worksheet.set_column('P:P', 10)
worksheet.set_column('Q:Q', 30)
worksheet.set_column('R:R', 10)

# 设置标题头样式，字体加粗，水平对齐,上下居中，边框1像素
titlecss = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 2,
                                'bg_color': 'blue','color': 'white', 'text_wrap': True})
contextcss = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})

title = ['稽核单编号', '基站编号', '基站名称', '是否已派单', '提交时间', '状态', '所属分公司', '退单次数',
         '省公司第一次退单原因', '第一次退单操作人', '省公司第二次退单原因', '第二次退单操作人', '省公司第三次退单原因', '第三次退单操作人',
         '省公司第四次退单原因', '第四次退单操作人', '省公司第五次退单原因', '第五次退单操作人']
worksheet.write_row('A1', title,titlecss)
num = 2
for item in order_list:

    a1 = item['orderId']
    a2 = item['stationId']
    a3 = item['stationName']
    a4 = item['sended']
    a5 = item['submitTime']
    a6 = item['status']
    a7 = item['company']
    a8 = item['rejectNum']

    tDict = item['rejectList']
    tList = []
    for item in tDict:
        if '不同意' in item['status']:
            tList.append(item['status'])
            tList.append(item['name'])

    if a7 == '中山分公司':
        # 如果出现“中山分公司”，抛弃该条数据
        continue

    dataRow = [a1, a2, a3, a4, a5, a6, a7, a8]
    dataRow = dataRow + tList
    # tmp_list = list(item.values())

    worksheet.write_row('A' + str(num), dataRow, contextcss)
    num = int(num) + 1

driver.quit()