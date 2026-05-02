#Пару строк кода, чтобы работать со временем

from datetime import datetime, timezone, timedelta

msk_timezone = timezone(timedelta(hours=3))

def epoch():
    return datetime.now(msk_timezone).timestamp()

def date():
    dtn = str(datetime.now(msk_timezone).date().today())
    res = f'{dtn[-2:]}.{dtn[-5:-3]}.{dtn[:4]}'
    return res

def time():
    h = str(datetime.now(msk_timezone).hour)
    if len(h) == 1:
        h = '0' + h
    m = str(datetime.now(msk_timezone).minute)
    if len(m) == 1:
        m = '0' + m
    s = str(datetime.now(msk_timezone).second)
    if len(s) == 1:
        s = '0' + s
    res = f'{h}:{m}:{s}'
    return res

def closest_monday(delta = 0):
    dtn = datetime.now(msk_timezone).date().today()
    dtn += timedelta(days=((0 - dtn.weekday()) % 7 + delta))
    dtn = str(dtn)
    res = f'{dtn[-2:]}.{dtn[-5:-3]}.{dtn[:4]}'
    return res

def day_sicne_epoch(delta = 0):
    now = datetime.now(timezone.utc)
    days_since_epoch = now.timestamp() // 86400
    days_since_epoch += delta
    return days_since_epoch