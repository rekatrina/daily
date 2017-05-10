# -*- coding:utf-8 -*-
import urllib2
import re
import time
import datetime
import MySQLdb

import local_settings as ls
import views

def get_html(url_):
    #print url_
    #url_ = url_.encode('utf-8')
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    urlreq = urllib2.Request(url=url_, headers=headers)
    req = urllib2.urlopen(urlreq)
    content = req.read()
    #print content.decode('utf-8').encode('utf-8')
    return content.decode('utf-8').encode('utf-8')


def get_column(cont, col):
    pattern = col+r'.*?</div>'
    tmp = re.findall(pattern, cont, flags = re.DOTALL)
    #print tmp[0].decode('utf-8').encode('utf-8')
    return tmp

def get_column_detail(cont, col):
    pattern = col+r'.*?class'
    tmp = re.findall(pattern, cont, flags = re.DOTALL)
    print tmp[0].decode('utf-8').encode('utf-8')
    return tmp

def get_news(cont):
    titles = re.findall(r'title="(.*?)"', cont, flags = re.DOTALL)
    href = re.findall(r'href="(.*?)"', cont, flags=re.DOTALL)

    for i in range(0,len(titles)-1):
        print titles[i].decode('utf-8').encode('utf-8')
        print href[i+1].decode('utf-8').encode('utf-8')
    return [titles, href]


def get_news_detail(col, type):
    url = "http://www.lmars.whu.edu.cn/newsnoticelist.jsp?type=" + urllib2.quote(col)
    cont = get_html(url)
    #cont = get_html("http://www.lmars.whu.edu.cn/newsnoticelist.jsp?type=")
    cont = re.findall(r'<ul class="list-list ling-list">(.*?)</ul>', cont, flags = re.DOTALL)
    news = re.findall(r'<li>(.*?)</li>', cont[0], flags = re.DOTALL)
    msg_new=[]

    for new in news:
        msg = {}
        msg['hyper'] = re.findall(r'href="(.*?)"', new)[0].decode('utf-8').encode('utf-8')
        msg['title'] = re.findall(r'>(.+?)<', new)[0].decode('utf-8').encode('utf-8')
        msg['date'] = re.findall(r'<span>(.*?)</span>', new)[0].decode('utf-8').encode('utf-8')
        msg['type'] = type
        if(not checksql(msg)):
            addnew2sql(msg)
            msg_new.append(msg)
    return msg_new

def addnew2sql(msg):
    db = MySQLdb.connect(ls.sql_host, ls.sql_usr, ls.sql_pw, ls.sql_db)
    cursor = db.cursor()
    #print "INSERT INTO lmars_news VALUES('%s', '%s', %d, '%s')"%(msg['title'], msg['hyper'], msg['type'], msg['date'])
    try:
        cursor.execute("INSERT INTO lmars_news VALUES('%s', '%s', %d, '%s')"%(msg['title'], msg['hyper'], msg['type'], msg['date']))
        db.commit()
    except:
        print "db insert failed!"
        db.rollback()
    db.close()

def readsql():
    db = MySQLdb.connect(ls.sql_host, ls.sql_usr, ls.sql_pw, ls.sql_db)
    cursor = db.cursor()

    cursor.execute("SELECT * FROM lmars_news")
    datas = cursor.fetchall()
    for data in datas:
        print data[0]
    db.close()

def checksql(msg):
    db = MySQLdb.connect(ls.sql_host, ls.sql_usr, ls.sql_pw, ls.sql_db)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM lmars_news WHERE title = '%s'"%(msg['title']))
    num = cursor.fetchone()
    isexist = (num[0]!=0)
    #print isexist
    return isexist

def get_news_all():
    news = get_news_detail("新闻", 1)
    news2 = get_news_detail("通知", 2)
    news3 = get_news_detail("科研成果", 3)
    news.extend(news2)
    news.extend(news3)
    return news


if __name__ == '__main__':
    all_cont = get_html('http://www.lmars.whu.edu.cn/')
    #print all_cont
    #col1 = get_column(all_cont, r"新闻资讯")
    # #get_news(col1[0])
    #views.send_wechat_msg(urllib2.quote("新闻资讯") + time.strftime('%Y-%m-%d', time.localtime(time.time())), "rekatrina")
    while True:
        try:
            news_add = get_news_all()
            print 1
            print news_add
            print len(news_add)
            #readsql()

            if (len(news_add) != 0):
                 print "lmars news "+ time.strftime('%Y-%m-%d', time.localtime(time.time()))
                 views.send_wechat_msg("lmars news "+ time.strftime('%Y-%m-%d', time.localtime(time.time())), "rekatrina|ludage|JessicaXu")

            for news_a in news_add:
                print "%s"%news_a['title']
                views.send_wechat_msg(news_a['title'] + ':   http://www.lmars.whu.edu.cn/' + news_a['hyper'], "rekatrina|ludage|JessicaXu")

            cur = datetime.datetime.now()
            next = cur.replace(hour=12, minute=0, second=0)

            if (cur >= next):
                delta = next + datetime.timedelta(days=1) - cur
            else:
                delta = next - cur
            print "wait %d seconds"%delta.seconds
            time.sleep(delta.seconds)

        except:
            import traceback
            print traceback.print_exc()
            views.send_wechat_msg("service failed! please check webguard.py", "rekatrina")
