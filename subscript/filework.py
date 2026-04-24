#Выделенный файл для работы с файлами

import pathlib
import os
import json
from datetime import date, datetime

base_path = str(pathlib.Path(__file__).parent.resolve())[:-10]
SESSION_PATH = f'{base_path}/sessions'
#Осторожно, костыль. [:-10] возвращает корневую папку всего проекта, несмотря на то, что этот файл лежит в папке subscript
#Возможно есть решение покрасивее. Но это тоже работает.

def return_image(path, placeholder):
    full_path = f"{base_path}/static/images/{path}.jpg"
    if os.path.exists(full_path):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

def getuser(email):
    users_path = f"{base_path}/users/{email}.json"
    if os.path.exists(users_path):
        with open(users_path, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    return False

def setuser(email, changes):
    users_path = f"{base_path}/users/{email}.json"
    with open(users_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(changes, indent = 4))

def setproduct(id, to):
    lst = getproductlist()
    lst[id] = to
    setproductlist(lst)

def getproduct(id):
    return getproductlist()[id]

def setquerylist(name, to):
    users_path = f"{base_path}/queries/{name}"
    with open(users_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(to, indent = 4))

def getquerylist(name):
    products_path = f"{base_path}/queries/{name}"
    if os.path.exists(products_path):
        with open(products_path, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    return False

def getproductlist():
    with open(f"{base_path}/products/modal.json", 'r', encoding='utf-8') as f:
        return json.loads(f.read())

def setproductlist(to):
    with open(f"{base_path}/products/modal.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(to, indent = 4))

def getglobalproductlist():
    with open(f"{base_path}/products/global.json", 'r', encoding='utf-8') as f:
        return json.loads(f.read())

def setglobalproductlist(to):
    with open(f"{base_path}/products/global.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(to, indent = 4))

def does_user_exist(email):
    if os.path.exists(f'{base_path}/users/{email}.json'):
        return True
    return False