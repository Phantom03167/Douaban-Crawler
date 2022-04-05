import jieba
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyecharts.options as opts
import seaborn as sns
from matplotlib.ticker import MultipleLocator
from pyecharts.charts import Pie
from pyecharts.commons.utils import JsCode
from scipy import stats
from wordcloud import WordCloud, ImageColorGenerator

plt.rcParams["font.sans-serif"] = ["Simsun"]  # 指定默认字体，解决中文显示为方框
plt.rcParams["axes.unicode_minus"] = False  # 解决保存图像是负号“-”显示为方框

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)


# 设置value的显示长度为100，默认为50
# pd.set_option('max_colwidth',100)

# 绘制评分人数饼状图
def draw_rating_pie(path):
    data = read_short_comments(path)
    rating = list(data["评价"].value_counts().index)  # 评价列表
    rating_counts = list(data["评价"].value_counts())  # 各评价对应人数列表
    # print(rating_counts)

    # 绘制饼状图
    plt.figure(dpi=300, figsize=(6, 6))
    plt.pie(x=rating_counts, labels=rating, autopct="%.1f%%")
    # plt.savefig("rating pie.svg", dpi=500)# 保存饼状图
    plt.show()


# 绘制评价人数动态饼状图
def draw_rating_dynamic_charts(path):
    data = read_short_comments(path)
    rating = list(data["评价"].value_counts().index)  # 评价列表
    rating_counts = list(data["评价"].value_counts())  # 各评价对应人数列表
    pie = Pie(init_opts=opts.InitOpts(width="1500px", height="750px"))
    pie.add("评分", list(zip(rating, rating_counts)), is_clockwise=False,
            label_opts=opts.LabelOpts(position="inside", font_size=18, formatter="{b}：{d}%"))
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="评价人数饼状图", pos_left="center", pos_top="3%",
                                  title_textstyle_opts=opts.TextStyleOpts(font_size=28)),
        legend_opts=opts.LegendOpts(pos_left="85%", pos_top="30%", orient="vertical", item_gap=20,
                                    item_width=40, item_height=25,
                                    textstyle_opts=opts.TextStyleOpts(font_size=15)),
        toolbox_opts=opts.ToolboxOpts(orient="vertical", pos_left="85%", pos_top="70%",
                                      feature=opts.ToolBoxFeatureOpts(
                                          save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(background_color="white",
                                                                                           pixel_ratio=2),
                                          data_zoom=opts.ToolBoxFeatureDataZoomOpts(is_show=False),
                                          magic_type=opts.ToolBoxFeatureMagicTypeOpts(is_show=False),
                                          brush=opts.ToolBoxFeatureBrushOpts(type_=[]))))
    pie.render("豆瓣评价中占比动态饼图.html")


# 生成评论词云
def generate_word_cloud(path):
    data = read_short_comments(path)
    words = " ".join(data["评论"])  # 将所有评论连起来
    jieba.load_userdict("ExclusiveWords.txt")  # 加载用户字段（专属词）
    words = jieba.cut(str(words), cut_all=False)  # 分词
    words = " ".join(words)  # 将分好的次连起来

    # 加载停词表
    # stopwords=None
    with open("StopWords.txt", "r", encoding="utf-8") as file:
        stopwords = file.readlines()
        stopwords = map(lambda x: x.strip(), stopwords)
        stopwords = set(stopwords)

    bg_img = plt.imread("Spider_man.webp")
    img_color = ImageColorGenerator(bg_img)

    wc = WordCloud(background_color="white", mask=bg_img, stopwords=stopwords, scale=10,
                   font_path="C:\Windows\Fonts\simsun.ttc").generate(words)
    wc.recolor(color_func=img_color)

    plt.figure(dpi=400, figsize=(20, 10))
    plt.imshow(wc)
    plt.axis("off")
    # plt.savefig("words cloud.svg", dpi=500)
    plt.show()


# 绘制影片评分分布图
def draw_rating_distribution(path):
    data = read_movie_info(path)
    sns.displot(data["评分"], kde=True).figure.set_size_inches(10, 10)

    plt.title("豆瓣影片评分分布", fontsize=30, loc="center", x=0.4, y=0.9)  # 标题
    # plt.suptitle("豆瓣影片评分分布",fontsize=30)
    plt.xlabel("豆瓣电影评分", fontdict={"fontsize": 20})  # 横坐标标签
    plt.ylabel("电影数量", fontdict={"fontsize": 20})  # 纵坐标标签
    plt.xlim((0, 10.4))  # 横坐标显示范围
    plt.xticks(np.arange(0, 11, 1))  # 横坐标刻度范围
    plt.minorticks_on()  # 显示副刻度
    plt.gca().xaxis.set_minor_locator(MultipleLocator(0.5))  # 横坐标副刻度精度
    plt.gca().yaxis.set_minor_locator(MultipleLocator(20))  # 纵坐标副刻度精度

    # plt.savefig("豆瓣电影评分分布.svg", dpi=500)
    plt.show()


# k-s假设检验评分是否服从正态分布
def ks_test(path):
    data = read_movie_info(path)
    avg = data["评分"].mean()  # 平均值
    std = data["评分"].std()  # 标准差

    # k-s检验
    ks = stats.kstest(data["评分"], "norm", (avg, std))
    print(ks)


# 分析烂片
def analysis_bad_movies(path, quantitle=0.15, **kwargs):
    data = read_movie_info(path)
    bad_movies = data[data["评分"] <= data.quantile(quantitle)["评分"]]
    if not kwargs.get("sort"):
        kwargs["sort"] = "评分"
    if not kwargs.get("ascending"):
        kwargs["ascending"] = True
    bad_movies = bad_movies.sort_values(by=kwargs["sort"], ascending=kwargs["ascending"])
    return bad_movies


# 统计各个影片某键值对应各项的数量
def count_movies_opt(movies: pd.DataFrame, column: str):
    column_count = dict()
    if column not in ["导演", "主演", "影片类型"]:
        raise Exception("统计类型错误！")

    for li in movies[column].str.split(","):
        for j in li:
            if column_count.get(j):
                column_count[j] = column_count[j] + 1
            else:
                column_count[j] = 1
    # print(column_count)
    return column_count


# 计算烂片数量较多的某键值对应各项的占比
def bad_movies_opt_ratio(path, column: str, num=5):
    data = read_movie_info(path)  # 获取全部电影信息
    bad_movies = analysis_bad_movies(path)  # 获取烂片电影信息

    all_movies_opt_count = count_movies_opt(data, column)  # 获取全部电影某键值对应各项的数量
    bad_movies_opt_count = count_movies_opt(bad_movies, column)  # 获取烂片某键值对应各项的数量

    bad_movies_opt_count = sorted(bad_movies_opt_count.items(), key=lambda x: (x[1], x[0]), reverse=True)  # 按数量降序排序
    if num > len(bad_movies_opt_count) or num == 0:
        num = len(bad_movies_opt_count)
    elif num < 0:
        num = 5
    bad_movies_opt_count = bad_movies_opt_count[0:num]
    bad_movies_opt_count = dict(bad_movies_opt_count)

    opt_ratio = dict()
    for key in bad_movies_opt_count:
        opt_ratio[key] = (bad_movies_opt_count[key], all_movies_opt_count[key])

    return opt_ratio


# 画烂片某键值对应各项占比饼状图
def draw_bad_movies_opt_ratio(path, column: str):
    opt_ratio = bad_movies_opt_ratio(path, column)
    data_name = ["烂片", "其余"]
    center_list = [["20%", "35%"], ["50%", "35%"], ["80%", "35%"], ["35%", "75%"], ["65%", "75%"]]
    radius = [90, 120]

    fn1 = """
        function(params) {
            if(params.name == '其余')
                return '\\n\\n\\n\\n\\n' + params.name + ' : ' + params.percent + '%';
            return params.name + '\\n\\n烂片 : ' + params.percent + '%';
        }
        """
    fn2 = """
            function(params) {
                if(params.name == '其余')
                    return params.seriesName + '<br/>' + params.name + '：' + params.value + '（' + params.percent + '%）';
                return params.name + '<br/>烂片：' + params.value + '（' + params.percent + '%）';
            }
            """
    i = 0

    pie = Pie(init_opts=opts.InitOpts(width="1500px", height="750px", bg_color="white"))
    for key in opt_ratio:
        pie.add(key + " ", list(zip([key, "其余"], [opt_ratio[key][0], opt_ratio[key][1] - opt_ratio[key][0]])),
                center=center_list[i], radius=radius,
                label_opts=opts.LabelOpts(position="center", font_size=15, formatter=JsCode(fn1)))
        i = i + 1
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="烂片数量前5的{}的数量占比".format(column), pos_left="center", pos_top="5%",
                                  title_textstyle_opts=opts.TextStyleOpts(font_size=30)),
        legend_opts=opts.LegendOpts(pos_left="right", pos_top="30%", orient="vertical", item_gap=20,
                                    item_width=40, item_height=25,
                                    textstyle_opts=opts.TextStyleOpts(font_size=15)),
        tooltip_opts=opts.TooltipOpts(formatter=JsCode(fn2)),
        toolbox_opts=opts.ToolboxOpts(orient="vertical", pos_left="right", pos_top="70%",
                                      feature=opts.ToolBoxFeatureOpts(
                                          save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(background_color="white",
                                                                                           pixel_ratio=2),
                                          data_zoom=opts.ToolBoxFeatureDataZoomOpts(is_show=False),
                                          magic_type=opts.ToolBoxFeatureMagicTypeOpts(is_show=False),
                                          brush=opts.ToolBoxFeatureBrushOpts(type_=[]))))
    pie.render("烂片数量前5的{}的数量占比.html".format(column))


# 读取单部影片短评数据
def read_short_comments(path):
    data = pd.read_csv(path, sep=";", index_col=0)
    # data.columns = ["昵称", "评价", "发表时间", "评论", "赞同数"]
    data = data.dropna()  # 去掉空值
    # print(data)
    return data


# 读取影片信息数据
def read_movie_info(path):
    data = pd.read_csv(path, sep=";", index_col=0)
    data = data.dropna()  # 去掉空值
    # print(data)
    return data


if __name__ == '__main__':
    # draw_rating_dynamic_charts("comments douban.csv")
    # draw_rating_distribution("movies info.csv")
    # ks_test("movies info.csv")
    # m=analysis_bad_films("movies info.csv")
    # print(m.count())
    # c = count_movies_opt(read_movie_info("movies info.csv"))
    # print(c)
    # d = bad_movies_opt_ratio("movies info.csv", "主演", 10)
    # print(d)
    # draw_bad_movies_opt_ratio("movies info.csv", "主演")

    pass
