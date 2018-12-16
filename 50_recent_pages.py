import re
import rsa
import time
import json
import base64
import logging
import binascii
import requests
import urllib.parse
from bs4 import BeautifulSoup
from util import date_process,forward_process,like_process,comment_process

#########################login

def get_username(user_name):
    """
    get legal username
    """
    username_quote = urllib.parse.quote_plus(user_name)
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))
    return username_base64.decode("utf-8")

def get_json_data(su_value,session):
    """
    get the value of "servertime", "nonce", "pubkey", "rsakv" and "showpin", etc
    """
    params = {
        "entry": "weibo",
        "callback": "sinaSSOController.preloginCallBack",
        "rsakt": "mod",
        "checkpin": "1",
        "client": "ssologin.js(v1.4.18)",
        "su": su_value,
        "_": int(time.time()*1000),
    }
    try:
        response = session.get("http://login.sina.com.cn/sso/prelogin.php", params=params)
        json_data = json.loads(re.search(r"\((?P<data>.*)\)", response.text).group("data"))
    except Exception as excep:
        json_data = {}
        logging.error("Login get_json_data error: %s", excep)
    logging.debug("Login get_json_data: %s", json_data)
    return json_data

def get_password(servertime, nonce, pubkey,pass_word):
    """
    get legal password
    """
    string = (str(servertime) + "\t" + str(nonce) + "\n" + str(pass_word)).encode("utf-8")
    public_key = rsa.PublicKey(int(pubkey, 16), int("10001", 16))
    password = rsa.encrypt(string, public_key)
    password = binascii.b2a_hex(password)
    return password.decode()


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s\t%(message)s")

user_name='18959216747'
pass_word='hao504137'
user_uniqueid=None
user_nick=None

session=requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"})

#get json data
s_user_name = get_username(user_name)
json_data = get_json_data(s_user_name,session)
if not json_data:
    logging.error('can not fetch json data')
    raise Exception
s_pass_word = get_password(json_data["servertime"],json_data["nonce"],json_data["pubkey"],pass_word)

#make post_data
post_data = {
    "entry": "weibo",
    "gateway": "1",
    "from": "",
    "savestate": "7",
    "userticket": "1",
    "vsnf": "1",
    "service": "miniblog",
    "encoding": "UTF-8",
    "pwencode": "rsa2",
    "sr": "1280*800",
    "prelt": "529",
    "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
    "rsakv": json_data["rsakv"],
    "servertime": json_data["servertime"],
    "nonce": json_data["nonce"],
    "su": s_user_name,
    "sp": s_pass_word,
    "returntype": "TEXT",
}

#get captcha code
if json_data["showpin"]==1:
    url="http://login.sina.com.cn/cgi/pin.php?r=%d&s=0&p=%s" % (int(time.time()),json_data["pcid"])
    with open("captcha.jpeg","wb") as file_out:
        file_out.write(session.get(url).content)
    code=input("please enter captcha:")
    post_data["pcid"]=json_data["pcid"]
    post_data["door"]=code

#login weibo.com
login_url_1 = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)&_=%d" % int(time.time())
json_data_1 = session.post(login_url_1,data=post_data).json()
if json_data_1["retcode"]=="0":
    params = {
        "callback": "sinaSSOController.callbackLoginStatus",
        "client": "ssologin.js(v1.4.18)",
        "ticket": json_data_1["ticket"],
        "ssosavestate": int(time.time()),
        "_": int(time.time()*1000),
    }
    response = session.get("https://passport.weibo.com/wbsso/login",params=params)
    json_data_2 = json.loads(re.search(r"\((?P<result>.*)\)",response.text).group("result"))
    if json_data_2["result"] is True:
        user_uniqueid = json_data_2["userinfo"]["uniqueid"]
        user_nick = json_data_2["userinfo"]["displayname"]
        logging.info("Login succeed: %s",json_data_2)
    else:
        logging.error("Login failed: %s",json_data_2)
else:
    logging.error("Login failed: %s",json_data_1)



#########################search

search_key = '转基因'

data=[]
for page in range(50):
    search_response = session.get('https://s.weibo.com/weibo?q=%s&nodup=1&page=%d' % (search_key,page+1))
    soup = BeautifulSoup(search_response.text)
    feed_list=soup.find_all(attrs={'action-type':'feed_list_item'})

    for feed_list_item in feed_list:

        feed_list_content = feed_list_item.find_all(attrs={'node-type':'feed_list_content'})

        #微博id
        mid = feed_list_item.attrs['mid']

        #用户uid
        avator = feed_list_item.find(attrs={'class':'avator'})
        person_url = avator.a.attrs['href']
        uid = re.match(r'//weibo.com/(\d+)', person_url).groups()[0]

        #转发数 评论数 点赞数
        card_act=feed_list_item.find(attrs={'class':'card-act'})
        feed_list_forward = card_act.find(attrs={'action-type':'feed_list_forward'})
        feed_list_comment = card_act.find(attrs={'action-type': 'feed_list_comment'})
        feed_list_like = card_act.find(attrs={'action-type': 'feed_list_like'})

        forward_num = forward_process(feed_list_forward.string)
        comment_num = comment_process(feed_list_comment.string)
        like_num = like_process(feed_list_like.em.string)

        #日期
        From = feed_list_item.find_all(attrs={'class': 'from'})
        if (len(From) == 1):
            date = From[0].a.contents
        else:
            date = From[len(From) - 1].a.contents
        date = date_process(date[0])

        #内容
        content = feed_list_item.find(attrs={'class':'content'})
        contentFirstP = content.p.contents[0]
        contentText = ''
        for i in contentFirstP:
            if(type(i)==type('str')):
                contentText = contentText+i
            else:
                contentText = contentText + i.string

        data.append({
            'mid':mid,
            'uid':uid,
            'date':date,
            'forward_num':forward_num,
            'comment_num': comment_num,
            'like_num': like_num,
            'content':contentText,
        })




# book = xlwt.Workbook(encoding='utf-8', style_compression=0)
# sheet = book.add_sheet('50_recent_pages',cell_overwrite_ok=True)
# sheet.write(0,0,'mid')
# sheet.write(0,1,'uid')
# sheet.write(0,2,'date')
# sheet.write(0,3,'forward_num')
# sheet.write(0,4,'comment_num')
# sheet.write(0,5,'like_num')
# sheet.write(0,6,'content')

# row = 1
# for i in data:
#     sheet.write(row,0,i['mid'])
#     sheet.write(row, 1, i['uid'])
#     sheet.write(row, 2, i['date'])
#     sheet.write(row, 3, i['forward_num'])
#     sheet.write(row, 4, i['comment_num'])
#     sheet.write(row, 5, i['like_num'])
#     sheet.write(row, 6, i['content'])
#     row=row+1
