获取广东移动物业管理平台，某项特定信息的爬虫
使用selenium来做自动化登陆和页面浏览，基于chrome插件的实现
校验码问题，目前的解决办法为人工手动输入
模态框的数据获取问题：目前的解决办法为，将该模态框显示的内容的连接重新分析出来，
然后再重新打开，打开的页面就是这个模态框的页面代码，这时在获取里面的代码和内容，


## 依赖的外部库
> beautifulsoup4==4.6.0 <br>
> bs4==0.0.1 <br>
> certifi==2018.4.16 <br>
> chardet==3.0.4 <br>
> configparser==3.5.0 <br>
> idna==2.6 <br>
> numpy==1.14.3 <br>
> opencv-python==3.4.0.12 <br>
> Pillow==5.1.0 <br>
> pytesseract==0.2.0 <br>
> requests==2.18.4 <br>
> selenium==3.11.0 <br>
> urllib3==1.22 <br>


依赖库可以通过命令安装：
```
pip install -r requirements.txt
```
requirements.txt文件包含在项目的根目录中

## 项目结构
* lib文件夹存放各类项目所需要的外部执行文件，包括webdriver插件
* data文件夹，保存获取后的文件就保存在这里
* tmp文件夹，存放校验码的临时文件夹，保存下来的校验码图片，使用ocr识别为字符串
* manual.md文件，项目的说明手册，同时也是开发文档。
* requirements.txt 项目所有依赖包及其精确的版本号的需求文件

## config.ini的配置
- url 广东移动物业管理平台的登陆网址地址
- username 登陆的用户名
- password 登陆的密码