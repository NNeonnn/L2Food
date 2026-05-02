#Выделенный файл для работы с файлами

import pathlib
import os
import json
import sqlite3

base_path = str(pathlib.Path(__file__).parent.resolve())[:-10]
SESSION_PATH = f'{base_path}/sessions'

def return_image(path, placeholder):
    full_path = f"{base_path}/static/images/{path}.jpg"
    if os.path.exists(full_path):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

class SQLInterface:
    def exec(self, query: str, args=(), output: bool = False):
        db = sqlite3.connect(base_path + '/products/database.db')
        cursor = db.cursor()
        cursor.execute(query, args)
        if (output):
            ans = cursor.fetchall()
            db.close()
            return ans
        db.commit()
        db.close()
    def to_dict(self, arr, template):
        if (len(arr) == 0):
            return dict()
        if (len(arr[0]) - 1 != len(template)):
            raise TypeError("Row length doesn't match template")
        ans = dict()
        for i in arr:
            ans[i[0]] = {}
            for j in range(len(template)):
                ans[i[0]][template[j]] = i[j + 1]
        return ans
    def to_arr_of_dicts(self, arr, template):
        if (len(arr) == 0):
            return []
        if (len(arr[0]) != len(template)):
            raise TypeError("Row length doesn't match template")
        ans = []
        for i in arr:
            ans.append(dict())
            for j in range(len(template)):
                ans[-1][template[j]] = i[j]
        return ans

globalProductlistTemplate = ["name", "category", "price", "description", "source", "volume_of_one"]
paymentTemplate = ["approved", "email", "amount"]

class GlobalProductlist(SQLInterface):
    def get_all(self):
        query = f"SELECT * FROM Global"
        return self.to_dict(self.exec(query, args=(), output=True), globalProductlistTemplate)
    def get_by_id(self, id: int):
        query = f"SELECT * FROM Global WHERE (id = ?)"
        return self.exec(query, args=(id), output=True)
    def insert(self, name: str, category: str, price: int, description: str, source: int):
        query = f"INSERT INTO Global (name, category, price, description, source) VALUES (?, ?, ?, ?, ?)"
        self.exec(query, args=(name, price, description, source))
    def erase(self, id: int): 
        query = f"DELETE FROM Global WHERE id = ?"
        self.exec(query, args=(id))
    def erase_source(self, src: int):
        query = f"DELETE FROM Global WHERE source = ?"
        self.exec(query, args=(src))

class ModalProductlist(SQLInterface):
    def get_all(self):
        ans = []
        for i in range(6):
            query = f"SELECT * FROM Global WHERE (id IN (SELECT global_id FROM Modal WHERE (day = ?)))"
            res = self.to_dict(self.exec(query, args=(i,), output=True), globalProductlistTemplate)
            ans.append(res)
        return ans
    def get_one(self, day, id):
        query = f"SELECT * FROM Global WHERE (id IN (SELECT global_id FROM Modal WHERE (day = ? AND modal_id = ?)))"
        res = self.to_dict(self.exec(query, args=(day, id), output=True), globalProductlistTemplate)
        return res[id]
    def insert(self, day: int, global_id: int):
        query = f"INSERT INTO Modal (global_id, day) VALUES (?, ?)"
        self.exec(query, args=(global_id, day))
    def erase(self, id: int): 
        query = f"DELETE FROM Modal WHERE id = ?"
        self.exec(query, args=(id))

class UserQueries(SQLInterface):
    def insert(self, day, user, id, quanity):
        query = f"INSERT INTO UserQueries (day, user, menu_id, quanity) VALUES (?, ?, ?, ?)"
        self.exec(query, args=(day, user, id, quanity))

class PaymentQueries(SQLInterface):
    def insert(self, user, amount):
        query = f"INSERT INTO PaymentQueries (email, amount) VALUES (?, ?)"
        self.exec(query, args=(user, amount))
    def get_all(self):
        query = f"SELECT approved, email, amount FROM PaymentQueries"
        return self.to_arr_of_dicts(self.exec(query, args=(), output=True), paymentTemplate)
    def count(self):
        query = f"SELECT COUNT(*) FROM PaymentQueries"
        return self.exec(query, args=(), output=True)[0][0]

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