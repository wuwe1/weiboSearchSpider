import re
from datetime import datetime,timedelta

def date_process(raw_date):
    now = datetime.now()
    time = re.match('\n                        (.*)\n',raw_date).groups()
    time = time[0]
    if(time.endswith('秒前')):
        time=time[:-2]
        time=int(time)
        result = now - timedelta(seconds=time)

    elif(time.endswith('分钟前')):
        time=time[:-3]
        time=int(time)
        result = now - timedelta(minutes=time)

    elif(time.startswith('今天')):
        time=time[2:]
        hour=time[:2]
        minute=time[3:]
        hour=int(hour)
        minute=int(minute)
        result = datetime(now.year,now.month,now.day,hour,minute)

    elif(('日' in time) and (':' in time)):
        month=int(time[:2])
        day=int(time[3:5])
        hour=int(time[7:9])
        minute=int(time[10:12])
        result=datetime(now.year,month,day,hour,minute)

    else:
        print('alie')

    return result

if __name__ == '__main__':
    print(date_process('\n                        1秒前\n'))
    print(date_process('\n                        1分钟前\n'))
    print(date_process('\n                        今天19:04\n'))
    print(date_process('\n                        12月08日\n'))