#Выделенный файл для работы с файлами

import pathlib
import os
import json
import pymongo

base_path = str(pathlib.Path(__file__).parent.resolve())[:-10]
SESSION_PATH = f'{base_path}/sessions'
MONGO_URL    = os.environ.get("MONGO_URL", "mongodb://user:pass@mongo:27017")
MONGO_DB     = os.environ.get("MONGO_DB", "canteen")

mongo_client = pymongo.MongoClient(MONGO_URL)
mongo_db = mongo_client[MONGO_DB]
users_collection = mongo_db["users"]

def return_image(path, placeholder):
    full_path = f"{base_path}/static/images/{path}.jpg"
    if os.path.exists(full_path):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

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

def getuser(email: str):
    #try:
    doc = users_collection.find_one({"email": email}, {"_id": 0})
    print(doc)
    return doc if doc else False
    #except Exception:
    #    return False

def setuser(email: str, changes: dict):
    changes["email"] = email
    try:
        users_collection.replace_one(
            {"email": email},
            changes,
            upsert=True
        )
    except Exception:
        pass

def does_user_exist(email: str) -> bool:
    try:
        return users_collection.count_documents({"email": email}) > 0
    except Exception:
        return False