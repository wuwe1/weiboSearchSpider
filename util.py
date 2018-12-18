import re
from datetime import datetime,timedelta

def date_process(raw_date):
    now = datetime.now()
    time = raw_date[0]

    if(time.endswith('秒前')):
        time=time[:-2]
        time=int(time)
        result = str(now - timedelta(seconds=time))

    elif(time.endswith('分钟前')):
        time=time[:-3]
        time=int(time)
        result = str(now - timedelta(minutes=time))

    elif(time.startswith('今天')):
        time=time[2:]
        hour=time[:2]
        minute=time[3:]
        hour=int(hour)
        minute=int(minute)
        result = str(datetime(now.year,now.month,now.day,hour,minute))

    elif(('月' in time)and(not('年' in time))):
        month=int(time[:2])
        day=int(time[3:5])
        hour=int(time[7:9])
        minute=int(time[10:12])
        result=str(datetime(now.year,month,day,hour,minute))

    elif(('年' in time)):
        year=int(time[:4])
        month=int(time[5:7])
        day=int(time[8:10])
        hour=int(time[12:14])
        minute=int(time[15:17])
        result=str(datetime(year,month,day,hour,minute))

    else:
        raise TypeError('date wrong')

    return result

def forward_process(forward):
    if(not forward):
        return 0
    else:
        return(int(forward))

def comment_process(comment):
    if(not comment):
        return 0
    else:
        return(int(comment))

def like_process(like):
    if(not like):
        return 0
    else:
        return int(like)


def card_comment_process(card_comment):
    if (card_comment == None):
        forwardedContent = ''
        return forwardedContent
    else:
        if (card_comment.find(attrs={'node-type': 'feed_list_content_full'}) == None):
            # 没有展开全文
            forwardedContentText = card_comment.find(attrs={'node-type': 'feed_list_content'})
        else:
            forwardedContentText = card_comment.find(attrs={'node-type': 'feed_list_content_full'})

    forwardedContent = ''
    for text in list(forwardedContentText.stripped_strings):
        forwardedContent = forwardedContent + text
    return forwardedContent

def txts_process(txts):
    if (len(txts) == 1):
        # 没有展开全文
        contentText = txts[0]
    elif (len(txts) == 2):
        # 展开全文
        contentText = txts[1]

    contentText = list(contentText.stripped_strings)

    content = ''
    for text in contentText:
        content = content + text
    return content


if __name__ == '__main__':
    print(date_process(['1秒前']))
    print(date_process(['1分钟前']))
    print(date_process(['今天19:04']))
    print(date_process(['12月08日 12月03日 22:59']))
    print(date_process(['2017年12月03日 22:58']))
