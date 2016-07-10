from urllib.request import Request
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from pymongo import MongoClient
from time import sleep
from urllib.parse import urlparse
from random import randrange
from threading import Lock, Thread
from queue import Queue
from atexit import register
from socket import timeout, setdefaulttimeout
import sys

from os import path
from os import mkdir

from bs4 import BeautifulSoup

# 网站根路径
baseUrl = "http://www.ja7lib.com/cn"
# 新话题
urlUpdate = baseUrl + "/vl_update.php"
# 新发行-有评论
urlNewRelease = baseUrl + "/vl_newrelease.php?&mode=1"
# 新发行-全部
urlNewReleaseAll = baseUrl + "/vl_newrelease.php?&mode=2"
# 新加入
urlNewEntries = baseUrl + "/vl_newentries.php"
# 最想要-上个月
urlMostWanted = baseUrl + "/vl_mostwanted.php?&mode=1"
# 最想要-全部
urlMostWantedAll = baseUrl + "/vl_mostwanted.php?&mode=2"
# 高评价-上个月
urlBestrated = baseUrl + "/vl_bestrated.php?&mode=1"
# 高评价-全部
urlBestratedAll = baseUrl + "/vl_bestrated.php?&mode=2"

# 最大页
maxPage = 5
# 当前页
currentPage = 1
# 是否完成
isFinish = 0
# 同步锁
lock = Lock()

client = MongoClient("localhost", 27017)
db = client.jav

# 这里对整个socket层设置超时时间
timeout = 30
setdefaulttimeout(timeout)


# 增加video链接
def get_video_urls(url, queue):
    try:
        # 将html转换成Python对象
        bsObj = get_pagebs(url)
        # 找到所有video的div标签
        videoTags = bsObj.find_all("div", class_="video")
        for videoTag in videoTags:
            try:
                # 获取第一个a标签
                href = videoTag.a["href"]
                # 获取链接绝对路径
                href = baseUrl + href[1:]
                # string为标签内的字符串
                videoNum = videoTag.find("div", class_="id").string
                # 在有可用空间之前阻塞
                queue.put({"videoNum": videoNum, "href": href}, 1)
            except Exception as e:
                print(str.format("Position:{0},Error:{1}", get_current_function_name(), e))
                continue
        print(url)
        # 使用global才能赋值全局变量
        global currentPage
        global isFinish
        currentPage = currentPage + 1
        if currentPage > maxPage:
            lock.acquire()
            isFinish = 1
            lock.release()
            print("get video urls done")
            return None
        bsNextPage = bsObj.find("a", class_="page next")
        if bsNextPage:
            nextPageUrl = baseUrl[:-3] + bsNextPage["href"]
            get_video_urls(nextPageUrl, queue)
    except Exception as e:
        print(str.format("Position:{0},Error:{1}", __name__, e))
        return None


# 获取当前函数名
def get_current_function_name():
    return sys._getframe(1).f_code.co_name


# 获取页面beautifulsoup对象
def get_pagebs(url):
    html = url_open(url)
    # 将html转换成Python对象
    bsObj = BeautifulSoup(html.decode("utf8"), "html.parser")
    return bsObj


# 打开网址读取返回信息
def url_open(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Host": urlparse(url).netloc
    }
    # 请求添加heads
    req = Request(url, headers=headers)

    try:
        request = urlopen(req)
        content = request.read()
        request.close()
        return content
    except HTTPError as e:
        print('-----HTTPError url:', e)
    except UnicodeDecodeError as e:
        print('-----UnicodeDecodeError url:', e)
    except URLError as e:
        print("-----urlError url:", e)
    except timeout as e:
        print("-----socket timout:", e)


# 添加video信息
def get_video_infos(queue):
    global isFinish
    while True:
        if isFinish == 1 and queue.empty():
            lock.acquire()
            isFinish = 2
            lock.release()
            print("get video infos done")
            return None
        try:
            val = queue.get(1)
            if not exist_video_db(val["videoNum"]):
                get_video_info(val["href"])
        except Exception as e:
            print(str.format("Position:{0},Error:{1}", get_current_function_name(), e))
            continue


def get_video_info(url):
    # 将html转换成Python对象
    bsObj = get_pagebs(url)
    video = {}
    video["title"] = bsObj.find(id="video_title").a.string
    video["imgUrl"] = bsObj.find(id="video_jacket_img")["src"]
    video["videoNum"] = bsObj.find(id="video_id").find("td", class_="text").string
    video["date"] = bsObj.find(id="video_date").find("td", class_="text").string
    video["length"] = bsObj.find(id="video_length").find("span", class_="text").string
    video["director"] = get_field_list(bsObj.find(id="video_director"))
    video["maker"] = get_field_list(bsObj.find(id="video_maker"))
    video["label"] = get_field_list(bsObj.find(id="video_label"))
    if bsObj.find(id="video_review"):
        video["review"] = bsObj.find(id="video_review").find("span", class_="score").string[1:-1]
    video["genres"] = get_field_list(bsObj.find(id="video_genres"))
    video["cast"] = get_field_list(bsObj.find(id="video_cast"))
    video["usersWanted"] = bsObj.find(id="subscribed").a.string
    video["usersWatched"] = bsObj.find(id="watched").a.string
    video["userOwned"] = bsObj.find(id="owned").a.string
    print(video)
    insert_video_db(video)


# 获取字段列表
def get_field_list(bsObj):
    list = []
    if bsObj:
        tags = bsObj.find("td", class_="text").find_all("a")
        for tag in tags:
            name = tag.string
            url = baseUrl + "/" + tag["href"]
            list.append({"name": name, "url": url})
    return list


# 增加video信息到数据库中
def insert_video_db(video):
    return db.videos.insert_one(video)


# 检查video是否存在数据库中
def exist_video_db(videoNum):
    return db.videos.find_one({"videoNum": videoNum})


# 下载图片
def download_imgs():
    # 图片保存路径
    save_path = path.abspath("./downlaods")
    if not path.exists(save_path):
        mkdir(save_path)

    while True:
        videoInfoList = find_download_videos_db()
        if isFinish == 2 and videoInfoList.count() == 0:
            print("download images done")
            return None
        for video in videoInfoList:
            download_img(video, save_path)
            sleep(randrange(1, 5))
        sleep(5)


def download_img(video, save_path):
    # 直到下载图片成功
    while True:
        try:
            filename = video["videoNum"] + '.jpg'
            filePath = path.join(save_path, filename)
            if not path.exists(filePath):
                image = url_open(video["imgUrl"])
                with open(filePath, "wb") as f:
                    f.write(image)
                print("Done: ", filename)
            # 更新已下载状态
            update_video_status_db(video, "downloaded")
            break
        except Exception as e:
            print(str.format("Position:{0},Error:{1}", get_current_function_name(), e))
            sleep(randrange(1, 5))


# 找到需要下载图片的video
def find_download_videos_db():
    return db.videos.find({"status": {"$nin": ["downloaded"]}})


# 更新video的状态已下载
def update_video_status_db(video, status):
    db.videos.update_one({"videoNum": video["videoNum"]}, {"$set": {"status": status}})


class MyThread(Thread):
    def __init__(self, func, args, name=""):
        Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def getResult(self):
        return self.res

    # 重写父类run方法，在线程启动后执行该方法内的代码。
    def run(self):
        self.res = self.func(*self.args)


def main():
    # 存储video队列
    pageQ = Queue(100)
    funcs = [get_video_urls, get_video_infos, download_imgs]
    threads = []
    for func in funcs:
        args = ()
        if func.__name__ == "get_video_urls":
            args = (urlBestrated, pageQ)
        elif func.__name__ == "get_video_infos":
            args = (pageQ,)
        t = MyThread(func, args, func.__name__)
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()


# 退出函数，会在脚本退出之前请求调用这个特殊函数
@register
def _atexit():
    print("all done")


if __name__ == "__main__":
    main()
