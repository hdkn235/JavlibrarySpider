from urllib.request import Request
from urllib.request import urlopen
from bs4 import BeautifulSoup

url = "http://www.ja7lib.com/cn/vl_update.php"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Host": "www.ja7lib.com"
}

req = Request(url, headers=headers)

# 打开网址
html = urlopen(req)

# 将html转换成Python对象
bsobj = BeautifulSoup(html.read().decode("utf8"),"html.parser")

print(bsobj.title)
