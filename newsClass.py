import pymysql.cursors
import datetime
import re
import requests
from bs4 import BeautifulSoup


def createTableToDB():
    connect = connectfunc()
    cursor = connect.cursor()

    sql = "create table news( \
           tid int not null auto_increment primary key, \
           title varchar(256), \
           link varchar(256), \
           img varchar(256), \
           isimg int not null, \
           remark int, \
           recorddate date)"
    cursor.execute(sql)
    print("Creat table completed!")

    cursor.close()
    connect.close()


def dropTableFromDB():

    connect = connectfunc()
    cursor = connect.cursor()

    sql = "DROP TABLE news"
    cursor.execute(sql)
    print("Drop table completed!")

    cursor.close()
    connect.close()


def insertToDB(title, href, img, imgtitle, imghref):

    now_time = datetime.datetime.now()
    rdate = now_time.strftime('%Y-%m-%d')

    connect = connectfunc()
    cursor = connect.cursor()

    sql = "INSERT INTO news(title, link, img, isimg, recorddate) VALUES (%s, %s, %s, %s, %s)"
    val = []
    for i in range(len(title)):
        temp = (title[i], href[i], '', 0, rdate)
        val.append(temp)

    for i in range(len(imgtitle)):
        temp = (imgtitle[i], imghref[i], img[i], 1, rdate)
        val.append(temp)

    cursor.executemany(sql, val)
    connect.commit()
    print("Insert data completed!")

    cursor.close()
    connect.close()


def selectFromDB(isGetRecord, sdate):
    connect = connectfunc()
    cursor = connect.cursor()

    # sql = "SELECT * FROM news where to_days(recorddate) = to_days(now()) order by tid"
    sql = "SELECT * FROM news where date(recorddate) = date('%s') order by tid" % (sdate)
    cursor.execute(sql)

    if isGetRecord == False:
        return cursor.rowcount

    title = []
    href = []
    img = []
    imgtitle = []
    imghref = []
    for row in cursor.fetchall():
        if row[4] == 0:
            title.append(row[1])
            href.append(row[2])
        if row[4] == 1:
            img.append(row[3])
            imgtitle.append(row[1])
            imghref.append(row[2])
    print('The number of selected record is', cursor.rowcount)

    cursor.close()
    connect.close()

    return title, href, img, imgtitle, imghref


def connectfunc():
    connect = pymysql.Connect(
        host='db4free.net',
        port=3306,
        user='yujiezs12',
        passwd='18666929531',
        db='remysql',
        charset='utf8'
    )
    return connect

def getlist(bs):

    recommended_movies = bs.find('div', {'class': 'op-news'})
    movie_list = recommended_movies.find_all('div', {'class': 'news'})

    title = []
    href = []
    for item in movie_list:
        title.append(item.find('a').get_text())
        href.append(item.find('a').get('href'))

    return title, href

def getpic(bs):

    top = bs.find('div', {'id': 'carousel-main-img'})
    img_list = top.find_all('div', {'class': 'item'})

    img = []
    imgtitle = []
    imghref = []
    for item in img_list:
        img.append(item.find('img', {'class': 'main_img'}).get('src'))
        next = item.find('div', {'class': 'main_caption'})
        imgtitle.append(next.find('a').get_text())
        imghref.append(next.find('a').get('href'))

    return img, imgtitle, imghref

def getNewsfromWeb():

    news ='https://www.globaltimes.cn//special-coverage/Coronavirus-Outbreak.html'
    html = requests.get(news)  # connect to the server
    bs = BeautifulSoup(html.text, 'html.parser')  # manage tags in HTML document

    title, href = getlist(bs)
    img, imgtitle, imghref = getpic(bs)

    return title, href, img, imgtitle, imghref


def get_news_data(msg):
    list = re.findall(r'\b\d+\b', msg)
    showinTilte = ''
    if len(list)>=2:
        if int(list[-2]) >= 1 and int(list[-2]) <= 12 and int(list[-1]) >= 1 and int(list[-1]) <= 31:
            fdata = "2020-" + list[-2] + "-" + list[-1]
            title, href, img, imgtitle, imghref = selectFromDB(True, fdata)
            showinTilte = ' in ' + list[-2] + "." + list[-1]
    else:
        title, href, img, imgtitle, imghref = getNewsfromWeb()

    return title, href, img, imgtitle, imghref, showinTilte


def insert_news_data(title, href, img, imgtitle, imghref):

    now_time = datetime.datetime.now()
    today_date = now_time.strftime('%Y-%m-%d')

    num = selectFromDB(False, today_date)
    if num == 0:
        insertToDB(title, href, img, imgtitle, imghref)