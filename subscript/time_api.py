#Пару строк кода, чтобы работать со временем

from datetime import datetime, timezone, timedelta

msk_timezone = timezone(timedelta(hours=3))

def epoch():
    return datetime.now(msk_timezone).timestamp()

def date():
    dtn = str(datetime.now(msk_timezone).date().today())
    res = f'{dtn[-2:]}.{dtn[-5:-3]}.{dtn[:4]}'
    return res

def closest_monday():
    dtn = datetime.now(msk_timezone).date().today()
    dtn += timedelta(days=(0 - dtn.weekday()) % 7)
    dtn = str(dtn)
    res = f'{dtn[-2:]}.{dtn[-5:-3]}.{dtn[:4]}'
    return res

def closest_saturday():
    dtn = datetime.now(msk_timezone).date().today()
    dtn += timedelta(days=(5 - dtn.weekday()) % 7)
    dtn = str(dtn)
    res = f'{dtn[-2:]}.{dtn[-5:-3]}.{dtn[:4]}'
    return res