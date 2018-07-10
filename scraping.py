'''
@Author : sean cheng
@Email  : aya234@163.com
@CreateTime   : 2018/5/3
'''
import configparser
import os
import re
import time

import selenium
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
# driver.get('http://10.251.147.207/complex/auditOrder/list.do')

driver.implicitly_wait(10)  # 浏览器智能等待10秒
driver.switch_to.frame("framecontent")  # 要获取到页面中的iframe，如果不这个做，获取元素或报错
# 重新提交条件搜索出内容
company = Select(driver.find_element_by_xpath('//*[@id="subBranch"]'))
company.select_by_index(0)
send_order = Select(driver.find_element_by_xpath('//*[@id="isSend"]'))
send_order.select_by_index(0)

page_length = Select(driver.find_element_by_xpath('//*[@id="data-table_length"]/label/select'))
page_length.select_by_visible_text('50')  # 显示100条数据，显示太少的话，请求会过于频繁。

driver.find_element_by_xpath('//*[@id="submitSearch"]').click()

time.sleep(20)  # 需要这样停数秒，才能获取到
page_num = driver.find_element_by_id('data-table_info').text
total_page = re.findall('共(.*)页', page_num)  # 通过正则表达式获取总页数
total_page = int(total_page[0].strip())  # 转为int类型
current_page = 1
url_all = []
order_list = []

# 循环执行，知道当前页的页码等于总页码（当前页小于总页码+1）
while current_page < total_page + 1:
    time.sleep(15)
    try:
        trs = driver.find_elements_by_xpath('//*[@id="data-table"]/tbody/tr')
    except:
        break

    for tr in trs:
        tr_html = tr.get_attribute('innerHTML')
        soup = BeautifulSoup(tr_html, 'html.parser')
        data_list = soup.find_all('td')
        url_list = data_list[-1].find_all('a')
        url = url_list[-1].get('href')

        url_fix = re.findall('"(.*)"', url)  # 通过正则表达式获取两个引号中的内容
        # 上面获取到的内容，是一个list，但实际只用一个值
        url_fix = config.get("basic", "base_url") + url_fix[0]  # 在前面加上基础的网址,组合成一段完整的网址

        order_dict = {}

        order_dict['orderId'] = data_list[0].text
        order_dict['stationId'] = data_list[1].text
        order_dict['stationName'] = data_list[2].text
        order_dict['sended'] = data_list[8].text
        order_dict['submitTime'] = data_list[9].text
        order_dict['status'] = data_list[10].text
        order_dict['company'] = data_list[11].text

        order_list.append(order_dict)

        url_all.append(url_fix)
        #  获取全部的内容，分离组合里面的查看里面的url出来，然后就直接重新打开这个页面
    try:
        driver.find_element_by_xpath('//*[@id="data-table_paginate"]/a[3]').click()  # 点击下一页，继续获取内容
        current_page += 1  # 当前页码加1
    except selenium.common.exceptions.WebDriverException:
        break

for item_url in url_all:
    # time.sleep(3)
    driver.get(item_url)  # 直接使用上面的分离出来的url打开为新页面，处理步骤的分页功能失效，直接加载了全部的步骤出来，方便了不用判断步骤的分页
    try:
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
        print(reject_list)
        #  查找不同意的次数
        for item in reject_list:
            if '不同意' in item['status']:
                examine_num += 1

        for item in order_list:
            if item['orderId'] == order_id:
                item['current_operator'] = processing_list[-1][1]
                item['rejectNum'] = examine_num
                item['rejectList'] = reject_list
    except:
        nowTime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        with open(os.path.abspath('error' + nowTime + '.txt'), 'a', encoding='utf-8') as file:
            file.write('无法访问的网址：' + item_url + '\n')
        continue

driver.quit()

# 内容写入excle文件中
filename = time.strftime('%Y%m%d', time.localtime(time.time()))
workbook = xlsxwriter.Workbook(os.path.abspath('data/' + filename + '.xlsx'))
worksheet = workbook.add_worksheet(filename)

# 设置列宽,
worksheet.set_column('A:A', 15)
worksheet.set_column('B:B', 15)
worksheet.set_column('C:C', 25)
worksheet.set_column('D:D', 8)
worksheet.set_column('E:E', 10)
worksheet.set_column('F:F', 16)
worksheet.set_column('G:G', 10)
worksheet.set_column('H:H', 10)
worksheet.set_column('I:I', 5)
worksheet.set_column('J:J', 30)
worksheet.set_column('K:K', 10)
worksheet.set_column('L:L', 30)
worksheet.set_column('M:M', 10)
worksheet.set_column('N:N', 30)
worksheet.set_column('O:O', 10)
worksheet.set_column('P:P', 30)
worksheet.set_column('Q:Q', 10)
worksheet.set_column('R:R', 30)
worksheet.set_column('S:S', 10)
worksheet.set_column('T:T', 30)
worksheet.set_column('U:U', 10)
worksheet.set_column('V:V', 30)
worksheet.set_column('W:W', 10)
worksheet.set_column('X:X', 30)
worksheet.set_column('Y:Y', 10)
worksheet.set_column('Z:Z', 30)
worksheet.set_column('AA:AA', 10)
worksheet.set_column('AB:AB', 30)
worksheet.set_column('AC:AC', 10)

# 设置标题头样式，字体加粗，水平对齐,上下居中，边框1像素
titlecss = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 2,
                                'bg_color': 'blue', 'color': 'white', 'text_wrap': True})
contextcss = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'border': 1, 'text_wrap': True})

title = ['稽核单编号', '基站编号', '基站名称', '是否已派单', '提交时间', '状态', '当前处理人', '所属分公司', '退单次数',
         '省公司第一次退单原因', '第一次退单操作人', '省公司第二次退单原因', '第二次退单操作人', '省公司第三次退单原因',
         '第三次退单操作人', '省公司第四次退单原因', '第四次退单操作人', '省公司第五次退单原因', '第五次退单操作人',
         '省公司第六次退单原因', '第六次退单操作人', '省公司第七次退单原因', '第七次退单操作人', '省公司第八次退单原因',
         '第八次退单操作人', '省公司第九次退单原因', '第九次退单操作人', '省公司第十次退单原因', '第十次退单操作人',
         ]
worksheet.write_row('A1', title, titlecss)
num = 2
for item in order_list:

    orderId = item['orderId']
    stationId = item['stationId']
    stationName = item['stationName']
    sended = item['sended']
    submitTime = item['submitTime']
    status = item['status']
    if 'current_operator' not in item.keys():
        current_operator = ''
    else:
        current_operator = item['current_operator']

    company = item['company']
    if 'rejectNum' not in item.keys():
        rejectNum = 0
    else:
        rejectNum = item['rejectNum']
    if 'rejectList' not in item.keys():
        tDict = [{'num': 0, 'name': '', 'time': '', 'status': ''}]
    else:
        tDict = item['rejectList']
    print(item['rejectList'])
    tList = []
    for item in tDict:
        if '不同意' in item['status']:
            tList.append(item['status'])
            tList.append(item['name'])

    if company == '中山分公司':
        # 如果出现“中山分公司”，抛弃该条数据
        continue

    # 如果退单的列表长度不够20，就在列表后面不20减去列表长度的数量的空格，目的是要让这些空白的单元格也有边框，属于文件的美化
    if len(tList) < 20:
        for i in range(20 - len(tList)):
            tList.append(' ')

    dataRow = [orderId, stationId, stationName, sended, submitTime, status, current_operator, company, rejectNum]
    dataRow = dataRow + tList

    worksheet.write_row('A' + str(num), dataRow, contextcss)
    num = int(num) + 1
