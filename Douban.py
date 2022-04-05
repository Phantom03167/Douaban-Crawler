import re
import sys
import time
import traceback
from urllib import parse

import json5
import requests
from bs4 import BeautifulSoup


# 通过豆瓣电影编号获取电影名
def get_movie_name(movie_id):
    url = "https://movie.douban.com/subject/" + movie_id + "/"
    res = requests.get(url, headers=header, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    film_name = soup.find("span", property="v:itemreviewed").text  # 影片名
    return film_name


# 获取短评数据（已看）
def get_comments_content(url, path):
    res = requests.get(url, headers=header, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    comments = soup.findAll("div", {"class": "comment-item"})

    for comment in comments:
        username = comment.find("a") and comment.find("a")["title"] or ""  # 用户名
        # rating = comment.find("span", class_="rating") and comment.find("span", {"class": "rating"})["title"] or ""
        rating = comment.find("span", class_="rating") and comment.find("span", class_="rating")["title"] or ""  # 评分
        # time = comment.find("span", class_="comment-time") and comment.find("span", class_="comment-time").text.split()[0] or ""
        time = comment.find("span", class_="comment-time") and \
               comment.find("span", class_="comment-time")["title"].split()[0] or ""  # 评论时间
        content = comment.find("span", class_="short") and comment.find("span", class_="short").text or ""  # 评论内容
        content = content.replace("\n", " ")
        vote = comment.find("span", class_="votes") and comment.find("span", class_="votes").text or ""  # 赞同数

        data = [username, rating, time, content, vote]
        data = ";".join(data) + "\n"
        # print(data)
        with open(path, "a", encoding='utf-8') as comments_file:
            comments_file.write(data)


# 获取影片短评数据
def get_short_comments(movie_id):
    path = get_movie_name(movie_id) + "_short_comments.csv"
    path = re.sub('[\\/:\*\?"<>\|]', " ", path)  # 去掉文件名中的非法字符
    with open(path, "w", encoding='utf-8'):
        columns = ["昵称", "评价", "发表时间", "评论", "赞同数"]
        columns = ";".join(columns) + "\n"

    num = input("请输入要获取评论的页数：")
    for i in range(int(num)):
        url = "https://movie.douban.com/subject/" + movie_id + "/comments?start=" + str(
            i * 20) + "&limit=20&status=P&sort=new_score"
        # print(url)

        print("正在获取第{}页数据......".format(str(i + 1)))
        get_comments_content(url, path)
        time.sleep(3)
    print("获取数据完成！")


# 获取单部影片信息
def get_movie_info(detail: dict, *, url=None, movie_id=None):
    if not (url or movie_id):
        raise Exception("无可获取的信息！")
    elif not url:
        url = "https://movie.douban.com/subject/" + movie_id + "/"

    res = None
    try:
        res = requests.get(url, headers=header, timeout=30)
    except:
        print(res.text)
        raise Exception(traceback.format_exception())
        return
    soup = BeautifulSoup(res.text, "html.parser")

    expr = {
        "film_name": "film_name = soup.find('span', property='v:itemreviewed') and soup.find('span', property='v:itemreviewed').text or ''  # 影片名\n" \
                     "data.append(film_name)",
        "director": "director = soup.find('a', rel='v:directedBy') and soup.findAll('a', rel='v:directedBy') or ''  # 导演\n" \
                    "director = list(map(lambda x: x.text, director))\n" \
                    "director = ','.join(director)\n" \
                    "data.append(director)",
        "main_actors": "main_actors = soup.find('span', class_='actor') and soup.find('span', class_='actor').findAll('a', rel='v:starring') or ''  # 主演\n" \
                       "main_actors = list(map(lambda x: x.text, main_actors))\n" \
                       "main_actors = ','.join(main_actors)\n" \
                       "data.append(main_actors)",
        "rate": "rate = soup.find('strong', class_='ll rating_num') and soup.find('strong', class_='ll rating_num').text or ''  # 评分\n" \
                "data.append(rate)",
        "film_type": "film_type = soup.find('span', property='v:genre') and soup.findAll('span', property='v:genre') or ''  # 影片类型\n" \
                     "film_type = list(map(lambda x: x.text, film_type))\n" \
                     "film_type = ','.join(film_type)\n" \
                     "data.append(film_type)",
        "rating_count": "rating_count = soup.find('span', property='v:votes') and soup.find('span', property='v:votes').text or ''  # 评分人数\n" \
                        "data.append(rating_count)",
        "rating_weight": "rating_weight = soup.find('span', class_='rating_per') and soup.findAll('span', class_='rating_per') or ''  # 评分比例（权重）\n" \
                         "rating_weight = list(map(lambda x: x.text, rating_weight))\n" \
                         "rating_weight = ','.join(rating_weight)\n" \
                         "data.append(rating_weight)",
        "short_comment_count": "short_comment_count = soup.find('div', id='comments-section').find('span', class_='pl').find('a') and soup.find('div', id='comments-section').find('span', class_='pl').find('a').text or ''  # 短评数\n" \
                               "short_comment_count = re.match('[\u4e00-\u9fa5]*\s([0-9]+)\s[\u4e00-\u9fa5]*', short_comment_count).group(1)\n" \
                               "data.append(short_comment_count)",
        "film_reviews_count": "film_reviews_count = soup.find('section', id='reviews-wrapper').find('span', class_='pl').find('a') and soup.find('section', id='reviews-wrapper').find('span', class_='pl').find('a').text or ''  # 影评数\n" \
                              "film_reviews_count = re.match('[\u4e00-\u9fa5]*\s([0-9]+)\s[\u4e00-\u9fa5]*', film_reviews_count).group(1)\n" \
                              "data.append(film_reviews_count)"
    }

    # 获取影片信息
    data = list()
    for key in detail:
        if detail[key]["get"]:
            exec(expr[key])

    # print(data)
    # print("获取电影信息完成！")
    return data


# 通过json文件获取影片信息
def get_movies_info_json(url, path, detail: dict, *, json_path=None):
    res = None
    for i in range(5):
        if url != '':
            res = requests.get(url, headers=header, timeout=30)
            res = res.text
        else:
            with open(json_path, "r", encoding="utf-8") as file:
                res = file.read()

        try:
            res = json5.loads(res)
        except:
            print(res.text + "\n")
            traceback.print_exc()
            time.sleep(3)
        else:
            break
        print("获取json文件失败！\nurl:{}".format(url))
        exit(1)

    expr = {
        "film_name": "film_name = item['title']  # 影片名\n" \
                     "data.append(film_name)",
        'director': "director = item['directors']  # 导演\n" \
                    "director = ','.join(director)\n" \
                    "data.append(director)",
        "main_actors": "main_actors = item['casts']  # 主演\n" \
                       "main_actors = ','.join(main_actors)\n" \
                       "data.append(main_actors)",
        "rate": "rate = item['rate']  # 评分\n" \
                "data.append(rate)"
    }

    data = list()
    n = 1
    if detail["film_type"]["get"] or \
            detail["rating_count"]["get"] or \
            detail["rating_weight"]["get"] or \
            detail["short_comment_count"]["get"] or \
            detail["film_reviews_count"]["get"]:  # 获取详细影片信息
        # j = 490
        # while j in range(len(res["data"])):
        #     item = res["data"][j]
        #     j=j+1
        for item in res["data"]:
            data = list()
            print("正在获取第{}条信息".format(n))
            n = n + 1
            movie_url = item["url"]
            for i in range(5):
                try:
                    data = get_movie_info(detail, url=movie_url)
                except:
                    print(data)
                    print("获取影片信息失败！\nurl:{}".format(movie_url))
                    traceback.print_exc()
                else:
                    break

            data = ";".join(data) + "\n"
            # print(data)
            with open(path, "a", encoding='utf-8') as file:
                file.write(data)
    else:  # 获取简略影片信息
        for item in res["data"]:
            data = list()
            print("正在获取第{}条信息".format(n))
            n = n + 1
            for key in detail:
                if detail[key]["get"]:
                    exec(expr[key])

                data = ";".join(data) + "\n"
                # print(data)
                with open(path, "a", encoding='utf-8') as file:
                    file.write(data)


# 获取多部影片信息
def get_movies_info(opt: list = ["film_name",
                                 "director",
                                 "main_actors",
                                 "film_type",
                                 "rate",
                                 "rating_count",
                                 "short_comment_count"]):
    path = "./movies info.csv"
    detail = {
        "film_name": {"get": True, "columns": "影片名"},
        "director": {"get": True, "columns": "导演"},
        "main_actors": {"get": True, "columns": "主演"},
        "film_type": {"get": True, "columns": "影片类型"},
        "rate": {"get": True, "columns": "评分"},
        "rating_count": {"get": True, "columns": "评分人数"},
        "rating_weight": {"get": False, "columns": "评分比例"},
        "short_comment_count": {"get": True, "columns": "短评数"},
        "film_reviews_count": {"get": False, "columns": "影评数"}
    }
    # 设置自定义内容
    if len(opt) != 0:
        with open(path, "w", encoding='utf-8') as file:
            for key in detail:
                if key in opt:
                    detail[key]["get"] = True
                    file.write(detail[key]["columns"] + ";")
                else:
                    detail[key]["get"] = False
            file.seek(file.tell()-1)
            file.truncate()
            file.write("\n")

    '''
        # 此接口信息较少，无导演
        base_url="https://movie.douban.com/j/search_subjects?"
        key_words = {
            "type": "movie",  # 类型  movie:电影 tv:电视剧
            "tag": "热门,华语,悬疑,中国大陆",  # 检索的标签（包括地区）
            # "playable": "1",  # 是否可以播放
            "sort": "rank",  # 排序方式  recommend:热度 time:时间 rank:评价
            "page_limit": "500",  # 每页获取的影片数（最大500）
            "page_start": "中国大陆",  # 检索的开始位置
        }
        '''

    base_url = "https://movie.douban.com/j/new_search_subjects?"
    key_words = {
        "sort": "T",  # 排序的方式 R:时间 S:评价 T:热度 U:混合热度（电影和电视剧）
        "range": "0,10",  # 电影评分的范围
        "tags": "",  # 检索的标签（地区、类型）可为空
        "start": 0,  # 检索的开始位置
        # "playable": 1,  # 是否可以播放 可省略
        # "unwatched": 1  # 是否还没看过 可省略
        # "genres": "喜剧",  # 类型 可省略
        # "countries": "中国大陆",  # 国家地区 可省略
        "limit": 500  # 每页电影数（尝试最大1500 太大会请求超时）
    }

    num = int(input("请输入要获取多少部电影的信息："))
    i = 0
    while (num > 0):
        key_words["start"] = str(i * key_words["limit"])
        if num < key_words["limit"]:
            key_words["limit"] = num
        key_url = parse.urlencode(key_words)  # url编码
        url = base_url + key_url  # 组合成完整的url
        # print(url)

        print("正在获取第{}页数据......".format(str(i + 1)))
        get_movies_info_json(url, path, detail)
        time.sleep(3)
        num = num - key_words["limit"]
        i = i + 1
    print("获取影片信息完成！")


if __name__ == '__main__':
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
        "Cookie": 'll="108090"; bid=8F5lp4M1Tp8; dbcl2="226951422:gX8xulp4d1A"; ck=EiWW; push_noty_num=0; push_doumail_num=0; ap_v=0,6.0'}

    detail = {
        "film_name": {"get": True, "columns": "影片名"},
        "director": {"get": True, "columns": "导演"},
        "main_actors": {"get": True, "columns": "主演"},
        "film_type": {"get": True, "columns": "影片类型"},
        "rate": {"get": True, "columns": "评分"},
        "rating_count": {"get": True, "columns": "评分人数"},
        "rating_weight": {"get": False, "columns": "评分比例"},
        "short_comment_count": {"get": True, "columns": "短评数"},
        "film_reviews_count": {"get": False, "columns": "影评数"}
    }
    # _movie_id = input("请输入豆瓣电影编号：")
    # print(get_movie_info(detail,url="https://movie.douban.com/subject/34812928/"))
    # get_movies_info()
    # get_movies_info_json("", "./movies info.csv", detail, json_path="./1000-1499.json")