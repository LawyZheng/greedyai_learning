import requests
import json
import random
import time
import datetime
import pandas
import re
import wordcloud
from sqlalchemy import create_engine


def get_browsers():
    url = 'https://fake-useragent.herokuapp.com/browsers/0.1.11'
    resp = requests.get(url)
    resp_json = json.loads(resp.text)
    browsers = resp_json['browsers']
    return browsers


def get_one_browser(browsers_dict):
    browsers_types = ['chrome', 'opera',
                      'firefox', 'internetexplorer', 'safari']
    browser_name = random.choice(browsers_types)
    return browsers_dict[browser_name][random.randint(0, len(browsers_dict[browser_name])-1)]


def set_headers_proxies(browsers):
    headers = {
        'user-agent': get_one_browser(browsers),
        'cookie': 'tt_webid=6728749993337783812;'\
                    ' WEATHER_CITY=%E5%8C%97%E4%BA%AC;'\
                    ' tt_webid=6728749993337783812;'\
                    ' csrftoken=9064ba1140ea772488719de5a8f1d63c;'\
                    ' __tasessionId=nrodt5w391566815101621;'\
                    ' RT="z=1&dm=toutiao.com&si=nq3huq73kj&ss=jzs9l18d&'\
                    'sl=1&tt=0&nu=638eb399121fab4a458c693663a49e01&'\
                    'cl=cjq&obo=1&ld=cjv&r=e146bfb383a8237828e0a8c1730f6177&ul=cjy&hd=cwo"'
    }

    proxies = {
        # 'https' :'185.20.163.138:8080'
    }

    return headers, proxies


def get_news_json(headers, proxies, time_stamp):
    url = 'https://www.toutiao.com/api/pc/feed/'

    # 设置url参数
    params = {
        'category': 'news_hot',
        'utm_source': 'toutiao',
        'widen': 1,
        'max_behot_time': time_stamp,
        'max_behot_time_tmp': time_stamp,
        'tadrequire': 'true',
        'as': 'A175CDF683C347A',
        'cp': '5D63C364C75A2E1',
        '_signature': '8Xb-MwAArB8fMKF4mbbhA.F2.i'
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.encoding = 'unicode_escape'

    #有时候需要用utf-8编码
    try:
        resp_json = json.loads(resp.text)
    except json.decoder.JSONDecodeError:
        resp.encoding = 'utf-8'
        resp_json = json.loads(resp.text)

    news_list = resp_json['data']

    # 如果获取新闻json数据失败，进行递归调用
    if not news_list:
        news_list = get_news_json(headers, proxies, time_stamp)

    return news_list


def get_article_tags(url, headers, proxies):
    try:
        resp = requests.get(url, headers=headers, proxies=proxies)
    except requests.exceptions.TooManyRedirects:
        # 更改user-agent
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'cookie': 'tt_webid=6728749993337783812;'\
                        ' WEATHER_CITY=%E5%8C%97%E4%BA%AC;'\
                        ' tt_webid=6728749993337783812;'\
                        ' csrftoken=9064ba1140ea772488719de5a8f1d63c;'\
                        ' __tasessionId=nrodt5w391566815101621;'\
                        ' RT="z=1&dm=toutiao.com&si=nq3huq73kj&ss=jzs9l18d&'\
                        'sl=1&tt=0&nu=638eb399121fab4a458c693663a49e01&'\
                        'cl=cjq&obo=1&ld=cjv&r=e146bfb383a8237828e0a8c1730f6177&ul=cjy&hd=cwo"'
        }
        resp = requests.get(url, headers=headers, proxies=proxies)

    article_tags = list()

    # 用正则表达式找到tags的json数据
    pattern = 'tags: (\[\{.+\}*\])'
    tags_json = re.findall(pattern, resp.text)

    # 如果该文章有标签
    if tags_json:
        tags = json.loads(tags_json[0])
        for tag in tags:
            article_tags.append(tag['name'])

    return article_tags


def save_to_database(dataframe):
    #连接数据库
    engine = create_engine('sqlite:///toutiao_hot.db')
    #engine = create_engine('sqlite:///test.db')
    print('数据库连接成功。')

    #取出数据库中原有的数据库
    df = pandas.read_sql('tb_toutiao_hot', con=engine, index_col='index')
    print('数据读取成功，正在进行数据清洗整合。')

    #将数据库中的json数据类型转化成python数据类型
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = list(map(json.loads, df[col]))

    #拼接新数据，并去重
    df_new = pandas.concat([df, dataframe], ignore_index=True, sort=False)
    df_new.drop_duplicates('item_id', keep='first', inplace=True)
    print('数据清洗整合完成，正在进行数据录入。')

    #将新数据转化成json类型
    for col in df_new.columns:
        if df_new[col].dtype == 'object':
            df_new[col] = list(map(json.dumps, df_new[col]))

    df_new.to_sql('tb_toutiao_hot', con=engine, if_exists='replace')
    print("数据录入成功。")


def toutiao_spider():
    visited = set()
    df = pandas.DataFrame()

    # 获取昨天和今天的时间
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    # 计算时间戳
    yesterday_start_time = int(time.mktime(
        time.strptime(str(yesterday), '%Y-%m-%d')))
    today_start_time = int(time.mktime(time.strptime(str(today), '%Y-%m-%d')))

    # 获取headers的user-agent
    browsers = get_browsers()

    # 爬取每隔半小时的数据
    for time_stamp in range(yesterday_start_time, today_start_time, 1800):
        #设置headers, proxies参数
        headers, proxies = set_headers_proxies(browsers)

        print("正在爬取数据。")
        #如果递归了很多次依旧没有找到数据，就跳过
        try:
            news_list = get_news_json(headers, proxies, time_stamp)
        except RecursionError:
            pass

        for news in news_list:
            # 如果已经访问过该新闻数据，则跳过
            if news['item_id'] in visited:
                continue
            # 偶尔会出现gallery之类只显示图片的网页数据。如果该内容不是文章，跳过
            if news['article_genre'] != 'article':
                continue
            #如果出现没有摘要的文章，一般都是图片，也跳过
            if not news['abstract']:
                continue

            # 添加到已访问
            visited.add(news['item_id'])

            # 重新设置头文件，获取文章的url
            headers, proxies = set_headers_proxies(browsers)
            url = "https://www.toutiao.com" + news['source_url']

            # 给新闻添加新的article_tags键
            try:
                news['article_tags'] = get_article_tags(url, headers, proxies)
            except:
                news['article_tags'] = list()

            # 给新闻添加被抓取的时间戳
            # append方法会将int类型转化成float类型, 所以格式化成datatime类型
            spider_time = datetime.datetime.fromtimestamp(time_stamp)
            news['spider_time'] = spider_time

            # 更新dataframe
            df = df.append(news, ignore_index=True)

        print("数据爬取成功。")
        print("已有数据%d条。" % len(visited))
        finished = ((time_stamp - yesterday_start_time) + 1800) / \
            (today_start_time - yesterday_start_time) * 100
        print("已完成进度: %.2f %%。" % finished)
        print("-"*30)

    #将behot_time转化成datetime格式
    df.behot_time = pandas.to_datetime(df.behot_time, unit='s')

    # 写入数据库
    #df.to_excel('toutiao_%04d%02d%02d.xlsx' % (today.year, today.month, today.day))
    print('爬取完成，准备录入数据库。')
    save_to_database(df)
    df.to_json('toutiao_%04d%02d%02d.json' % (today.year, today.month, today.day))


def create_wordcloud():
    engine = create_engine('sqlite:///toutiao_hot.db')
    df = pandas.read_sql('tb_toutiao_hot', con=engine, index_col='index')

    #将json数据转化成Python数据
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = list(map(json.loads, df[col]))

    # 获取文章abstract数据
    abstract_list = df.abstract.to_list()
    abstract = "\n".join(abstract_list)

    # 获取文章的tags数据
    tags_list = df.article_tags.to_list()
    tags = '\n'.join([' '.join(l) for l in tags_list])

    #清洗数据
    stopwords = {'人生第一份工作', '胜利退出演艺圈', '我的第一部5G手机',
                 '广州恒大淘宝足球俱乐部', '跳槽那些事儿', '越投入越精彩', '不完美妈妈', '原汁原味的德系SUV'}
    wc = wordcloud.WordCloud(font_path='msyh.ttf', stopwords=stopwords)

    wc.generate(abstract + tags)
    image = wc.to_image()
    image.show()

    # wc.generate(abstract)
    # image = wc.to_image()
    # image.show()

    # wc.generate(tags)
    # image = wc.to_image()
    # image.show()


if __name__ == '__main__':
    toutiao_spider()
    #create_wordcloud()
