from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import request

# 使用phantomjs浏览器
driver = webdriver.PhantomJS(executable_path=
                             r"E:\Lib\phantomjs-2.1.1-windows\bin\phantomjs.exe")

headers ={
    "Accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, * / *;q = 0.8",
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'Cache-Control':'max-age=0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    'Host':'hao.wxb.com',
    'Referer':'http://hao.wxb.com/'
}

# 添加headers
for key,value in enumerate(headers):
    webdriver.DesiredCapabilities.PHANTOMJS["phantomjs.page.customHeaders.{}".format(key)]=value

driver.get("http://hao.wxb.com/account/detail/2398278280")
try:
    # 等待直到页面通过ajax显示出数据
    element = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.CLASS_NAME,"li-main"))
    )
    pageSource = driver.page_source
    bsObj = BeautifulSoup(pageSource, "html.parser")
    links = bsObj.find_all("div", class_="li-main")
    for link in links:
        print(link.a["href"])
        # response = request.urlopen(link.a["href"])
        # content = response.read()
        # response.close()
        # bsObj = BeautifulSoup(content,"html.parser")
        # print(bsObj.find(id="activity-name").text)
        # time.sleep(3)
finally:
    driver.quit()

