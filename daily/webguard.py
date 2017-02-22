# -*- coding:utf-8 -*-
import urllib2
import re

import MySQLdb

import local_settings as ls
import views

def get_html(url):
    req = urllib2.urlopen(url)
    content = req.read()
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
    cont = get_html("http://www.lmars.whu.edu.cn/newsnoticelist.jsp?type=%s"%(col))
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

    #col1 = get_column(all_cont, r"新闻资讯")
    # #get_news(col1[0])

    news_add = get_news_all()
    print len(news_add)
    #readsql()

    for news_a in news_add:
        print news_a
        print "%s"%news_a['title']
        views.send_wechat_msg(news_a['title']+':   http://www.lmars.whu.edu.cn/'+news_a['hyper'], "ludage|rekatrina")


    views.send_wechat_msg("ludage", "ludage|rekatrina")