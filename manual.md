获取广东移动物业管理平台，某项特定信息的爬虫
使用selenium来做自动化登陆和页面浏览，tesseract-ocr做验证码的识别

## 依赖的外部库
> beautifulsoup4==4.6.0 <br>
> bs4==0.0.1 <br>
> configparser==3.5.0 <br>
> Pillow==5.1.0 <br>
> pytesseract==0.2.0 <br>
> selenium==3.11.0 <br>

依赖库可以通过命令安装：
```
pip install -r requirements.txt
```
requirements.txt文件包含在项目的根目录中

## 项目结构
* lib文件夹存放各类项目所需要的外部执行文件，包括tesseract免安装绿色版和webdriver插件
* data文件夹，保存获取后的文件就保存在这里
* manual.md文件，项目的说明手册，同时也是开发文档。
* requirements.txt 项目所有依赖包及其精确的版本号的需求文件

## config.ini的配置
- url 广东移动物业管理平台的登陆网址地址
- username 登陆的用户名
- password 登陆的密码