'''
@Author : sean cheng
@Email  : aya234@163.com
@CreateTime   : 2018/5/3
'''
import configparser
import cv2
import os
from time import sleep

import requests
from PIL import Image, ImageEnhance
from pytesseract import image_to_string
from selenium import webdriver
from selenium.webdriver.support.select import Select

config = configparser.ConfigParser()
config.read_file(open('config.ini','r'))


driver = webdriver.Chrome(executable_path=os.path.abspath('./lib/chromedriver.exe'))
driver.set_window_size(1366, 768)
driver.get(config.get("basic","url"))

# driver.save_screenshot('tmp/screenshot.png')  # 截图，为后面的获取校验码准备
#
# # 获取校验码区域，并计算出四个值，后面用这些值，裁剪截图，得到校验码，用于ocr
# source_image = driver.find_element_by_xpath('/html/body/div/div/div[2]/div/form/div[4]/img')
# img_left = int(source_image.location['x'])
# img_top = int(source_image.location['y'])
# img_right = int(source_image.location['x'] + source_image.size['width'])
# img_bottom = int(source_image.location['y'] + source_image.size['height'])
#
# # 裁剪区域，得到验证码的部分，用于后面ocr
# im = Image.open('tmp/screenshot.png')
# im = im.crop((img_left, img_top, img_right, img_bottom))
# im = ImageEnhance.Brightness(im).enhance(1.47)
# im.save('tmp/validata.png')
#
# img = cv2.imread('tmp/validata.png')
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #灰度化
# img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 1)  #二值化
#
# # 去噪声处理
# h, w = img.shape[:2]
# for y in range(1, w-1):
#     for x in range(1, h-1):
#         count = 0
#         if img[x, y-1] > 245:
#             count = count+1
#         if img[x, y+1] > 245:
#             count = count+1
#         if img[x-1, y] > 245:
#             count = count + 1
#         if img[x+1, y] > 245:
#             count = count+1
#         if count > 2:
#             img[x, y] = 255
#
# # 点降噪
# cur_pixel = img[x, y]  # 当前像素点的值
# height, width = img.shape[:2]
#
# for y in range(0, width - 1):
#     for x in range(0, height - 1):
#         if y == 0:  # 第一行
#             if x == 0:  # 左上顶点,4邻域
#                 # 中心点旁边3个点
#                 sum = int(cur_pixel) \
#                       + int(img[x, y + 1]) \
#                       + int(img[x + 1, y]) \
#                       + int(img[x + 1, y + 1])
#                 if sum <= 2 * 245:
#                     img[x, y] = 0
#             elif x == height - 1:  # 右上顶点
#                 sum = int(cur_pixel) \
#                       + int(img[x, y + 1]) \
#                       + int(img[x - 1, y]) \
#                       + int(img[x - 1, y + 1])
#                 if sum <= 2 * 245:
#                     img[x, y] = 0
#             else:  # 最上非顶点,6邻域
#                 sum = int(img[x - 1, y]) \
#                       + int(img[x - 1, y + 1]) \
#                       + int(cur_pixel) \
#                       + int(img[x, y + 1]) \
#                       + int(img[x + 1, y]) \
#                       + int(img[x + 1, y + 1])
#                 if sum <= 3 * 245:
#                     img[x, y] = 0
#         elif y == width - 1:  # 最下面一行
#             if x == 0:  # 左下顶点
#                 # 中心点旁边3个点
#                 sum = int(cur_pixel) \
#                       + int(img[x + 1, y]) \
#                       + int(img[x + 1, y - 1]) \
#                       + int(img[x, y - 1])
#                 if sum <= 2 * 245:
#                     img[x, y] = 0
#             elif x == height - 1:  # 右下顶点
#                 sum = int(cur_pixel) \
#                       + int(img[x, y - 1]) \
#                       + int(img[x - 1, y]) \
#                       + int(img[x - 1, y - 1])
#
#                 if sum <= 2 * 245:
#                     img[x, y] = 0
#             else:  # 最下非顶点,6邻域
#                 sum = int(cur_pixel) \
#                       + int(img[x - 1, y]) \
#                       + int(img[x + 1, y]) \
#                       + int(img[x, y - 1]) \
#                       + int(img[x - 1, y - 1]) \
#                       + int(img[x + 1, y - 1])
#                 if sum <= 3 * 245:
#                     img[x, y] = 0
#         else:  # y不在边界
#             if x == 0:  # 左边非顶点
#                 sum = int(img[x, y - 1]) \
#                       + int(cur_pixel) \
#                       + int(img[x, y + 1]) \
#                       + int(img[x + 1, y - 1]) \
#                       + int(img[x + 1, y]) \
#                       + int(img[x + 1, y + 1])
#
#                 if sum <= 3 * 245:
#                     img[x, y] = 0
#             elif x == height - 1:  # 右边非顶点
#                 sum = int(img[x, y - 1]) \
#                       + int(cur_pixel) \
#                       + int(img[x, y + 1]) \
#                       + int(img[x - 1, y - 1]) \
#                       + int(img[x - 1, y]) \
#                       + int(img[x - 1, y + 1])
#
#                 if sum <= 3 * 245:
#                     img[x, y] = 0
#             else:  # 具备9领域条件的
#                 sum = int(img[x - 1, y - 1]) \
#                       + int(img[x - 1, y]) \
#                       + int(img[x - 1, y + 1]) \
#                       + int(img[x, y - 1]) \
#                       + int(cur_pixel) \
#                       + int(img[x, y + 1]) \
#                       + int(img[x + 1, y - 1]) \
#                       + int(img[x + 1, y]) \
#                       + int(img[x + 1, y + 1])
#                 if sum <= 4 * 245:
#                     img[x, y] = 0
#
# cv2.imwrite('tmp/validata2.png', img)
#
# print('校验码识别:', image_to_string(Image.open('tmp/validata2.png'), lang='eng', config='-psm 4'))


driver.find_element_by_xpath('//*[@id="name"]').send_keys(config.get("basic","username"))
driver.find_element_by_xpath('/html/body/div/div/div[2]/div/form/div[3]/input').send_keys(config.get("basic","password"))



sleep(10)
driver.find_element_by_xpath('/html/body/div/div/div[2]/div/form/div[5]/a').click()

driver.find_element_by_xpath('//*[@id="header"]/div[3]/div/div/ul/li[5]/a').click()
driver.find_element_by_xpath('//*[@id="submenus160"]/li[2]/a').click()

sleep(5)
driver.switch_to.frame("framecontent") # 要获取到页面中的iframe，如果不这个做，获取元素或报错
# 重新提交条件搜索出内容
company = Select(driver.find_element_by_xpath('//*[@id="subBranch"]'))
company.select_by_index(0)

# page_length = Select(driver.find_element_by_xpath('//*[@id="data-table_length"]/label/select'))
# page_length.select_by_visible_text('1000')

driver.find_element_by_xpath('//*[@id="submitSearch"]').click()

sleep(5)
# ltxt = driver.find_elements_by_xpath('//*[@id="data-table"]/tbody/tr')

# driver.execute_script('javascript:$.saas.page.open({src:"/complex/auditOrder/view.do?processType=jh&orderId=3fa548f017e345cc95a9e8e56f98dfd6&processId=40"});')
driver.find_element_by_xpath('//*[@id="data-table"]/tbody/tr[2]/td[14]/a').click()  # 点击获取详情
# sleep(5)

driver.switch_to.default_content()
# driver.switch_to.alert()
# driver.find_element_by_xpath('//*[@id="tbody_1"]/table/tbody/tr[2]/td[2]')
driver.get('http://10.251.147.207/complex/auditOrder/view.do?processType=jh&orderId=898005e512ba4ddcbd74ff3abcb8d24d&processId=40')


# driver.quit()