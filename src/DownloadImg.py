from urllib.request import Request
from urllib.request import urlopen
from urllib.error import HTTPError

from os import path
from os import mkdir

from bs4 import BeautifulSoup

# 网站根路径
baseUrl = "http://www.ja7lib.com/cn"
# 新话题
urlUpdate = "http://www.ja7lib.com/cn/vl_update.php"
# 新发行-有评论
urlNewRelease = "http://www.ja7lib.com/cn/vl_newrelease.php?&mode=1"
# 新发行-全部
urlNewReleaseAll = "http://www.ja7lib.com/cn/vl_newrelease.php?&mode=2"
# 新加入
urlNewEntries = "http://www.ja7lib.com/cn/vl_newentries.php"
# 最想要-上个月
urlMostWanted = "http://www.ja7lib.com/cn/vl_mostwanted.php?&mode=1"
# 最想要-全部
urlMostWantedAll = "http://www.ja7lib.com/cn/vl_mostwanted.php?&mode=2"
# 高评价-上个月
urlBestrated = "http://www.ja7lib.com/cn/vl_bestrated.php?&mode=1"
# 高评价-全部
urlBestratedAll = "http://www.ja7lib.com/cn/vl_bestrated.php?&mode=2"
# 存储video未爬过链接
videoDicNew = {}
# 存储已下载的video信息
videoInfoList = {}
# 最大页
maxPage = 2
# 当前页
currentPage = 1


# 增加video链接
def add_video_urls(url):
    try:
        # 将html转换成Python对象
        bsObj = get_pagebs(url)
        # 找到所有video的div标签
        videoTags = bsObj.find_all("div", class_="video")
        for videoTag in videoTags:
            # 获取第一个a标签
            href = videoTag.a["href"]
            if href:
                # 获取链接绝对路径
                href = baseUrl + href[1:]
            # string为标签内的字符串
            name = videoTag.find("div", class_="id").string
            if not name in videoDicNew:
                videoDicNew[name] = href
        # 使用全局变量才能赋值
        global currentPage
        currentPage = currentPage + 1
        if currentPage > maxPage:
            return None
        bsNextPage = bsObj.find("a", class_="page next")
        if bsNextPage:
            nextPageUrl = baseUrl[:-3] + bsNextPage["href"]
            add_video_urls(nextPageUrl)
    except AttributeError as e:
        print(e)
        return None

# 获取页面beautifulsoup对象
def get_pagebs(url):
    html = url_open(url)
    try:
        # 将html转换成Python对象
        bsObj = BeautifulSoup(html.decode("utf8"), "html.parser")
        return bsObj
    except AttributeError as e:
        print(e)
        return None

# 打卡网址读取返回信息
def url_open(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Host": "www.ja7lib.com"
    }
    # 请求添加heads
    req = Request(url, headers=headers)

    try:
        response = urlopen(req)
        return response.read()
    except HTTPError as e:
        print(e)
        return None


# 添加video信息
def add_video_infos():
    if videoDicNew.__len__() == 0:
        print("page url can not be found")
        return None

    try:
        for name in videoDicNew:
            # 将html转换成Python对象
            bsObj = get_pagebs(videoDicNew[name])
            video = {}
            video["title"] = bsObj.find(id="video_title").a.string
            video["img"] = bsObj.find(id="video_jacket_img")["src"]
            video["id"] = bsObj.find(id="video_id").find("td", class_="text").string
            video["date"] = bsObj.find(id="video_date").find("td", class_="text").string
            video["length"] = bsObj.find(id="video_length").find("span", class_="text").string
            video["director"] = get_field_list(bsObj.find(id="video_director"))
            video["maker"] = get_field_list(bsObj.find(id="video_maker"))
            video["label"] = get_field_list(bsObj.find(id="video_label"))
            if bsObj.find(id="video_review"):
                video["review"] = bsObj.find(id="video_review").find("span", class_="score").string
            video["genres"] = get_field_list(bsObj.find(id="video_genres"))
            video["cast"] = get_field_list(bsObj.find(id="video_cast"))
            video["usersWanted"] = bsObj.find(id="subscribed").a.string
            video["usersWatched"] = bsObj.find(id="watched").a.string
            video["userOwned"] = bsObj.find(id="owned").a.string
            print(video)
            videoInfoList[name] = video
    except AttributeError as e:
        print(e)
        return None


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


# 下载图片
def download_imgs():
    if videoInfoList.__len__() == 0:
        return None
        print("img url can not be found")
    # 图片保存路径
    save_path = path.abspath("./downlaod")
    if not path.exists(save_path):
        mkdir(save_path)

    print("download begin...")

    for name in videoInfoList:
        filename = videoInfoList[name]["id"] + '.jpg'
        filePath = path.join(save_path, filename)
        if not path.exists(filePath):
            image = url_open(videoInfoList[name]["img"])
            with open(filePath, "wb") as f:
                f.write(image)
            print("Done: ", filename)

    print("download end...")


if __name__ == "__main__":
    add_video_urls(urlBestrated)

    add_video_infos()

    download_imgs()
