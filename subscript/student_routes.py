#Выделенный файл для всех путей, связанных с учениками (корзина, получение заказов, оплата)

from flask import render_template, request, redirect, url_for, send_file, session, render_template_string
from subscript.filework import *
from subscript.account_system import *
import subscript.time_api as time_api
from datetime import datetime

def get_cart_objects(email):
    user = getuser(email)
    if not user or 'cart' not in user:
        return [[], [], [], [], [], []], 0
    cart_ids = user['cart']
    all_products = getproductlist()
    cart_items = [[], [], [], [], [], []]
    total_price = 0
    for day in range(6):
        for item_id in cart_ids[day]:
            if item_id[0] in all_products[day]:
                item = all_products[day][item_id[0]]
                cart_items[day].append([item, item_id[1]])
                try:
                    total_price += int(item['price']) * item_id[1]
                except:
                    pass
    return cart_items, total_price

def gotfood(id):
    email = getlogin()
    kwargs = commonkwargs(email)
    id = int(id)
    if (kwargs['rights'] != 1):
        return redirect(url_for('dashboard'))
    user = getuser(email)
    new_to_take = []
    for i in user['to_take']:
        if (i['id'] != id):
            new_to_take.append(i)
    user['to_take'] = new_to_take
    setuser(email, user)
    admin_qu = getquerylist('student_buys.json')
    for i in range(len(admin_qu)):
        if (admin_qu[i]['id'] == id):
            admin_qu[i]['isComplete'] = True
            break
    setquerylist(name='student_buys.json', to=admin_qu)
    return redirect(url_for('dashboard'))

def add_to_cart():
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'))
    day = int(request.args.get('day', default = -1))
    id = int(request.args.get('id', default = -1))
    if day == -1 or id == -1:
        return redirect(url_for('dashboard'))
    user = getuser(email)
    if 'cart' not in user:
        user['cart'] = [[], [], [], [], [], []]
    for i in range(len(user['cart'][day])):
        if (user['cart'][day][i][0] == str(id)):
            user['cart'][day][i][1] += 1
            setuser(email, user)
            return redirect(url_for('dashboard'))
    user['cart'][day].append([str(id), 1])
    setuser(email, user)
    return redirect(url_for('dashboard'))

def remove_from_cart():
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'))
    day = int(request.args.get('day', default = -1))
    id = int(request.args.get('id', default = -1))
    if day == -1 or id == -1:
        return redirect(url_for('dashboard'))
    user = getuser(email)
    if 'cart' not in user:
        user['cart'] = [[], [], [], [], [], []]
    for i in range(len(user['cart'][day])):
        if (user['cart'][day][i][0] == str(id)):
            user['cart'][day][i][1] -= 1
            if user['cart'][day][i][1] == 0:
                user['cart'][day].remove(user['cart'][day][i])
            setuser(email, user)
            return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

def clear_cart():
    email = getlogin()
    if email != 'placeholder':
        user = getuser(email)
        user['cart'] = [[], [], [], [], [], []]
        setuser(email, user)
    return redirect(url_for('dashboard'))

def buy_from_cart():
    email = getlogin()
    user = getuser(email)
    if email == 'placeholder' or user['rights'] != 1:
        return redirect(url_for('login'))
    sum = 0
    dt = getquerylist("global.json")
    nowid = dt['total_student_queries']
    dt['total_student_queries'] += 1
    setquerylist(name="global.json", to=dt)
    productlist = getproductlist()
    names = [[], [], [], [], [], []]
    for day in range(6):
        for i in user['cart'][day]:
            if (i[1] == 1):
                names[day].append(productlist[day][i[0]]['name'])
                sum += productlist[day][i[0]]['price']
            else:
                names[day].append(f"{productlist[day][i[0]]['name']} x{i[1]}")
                sum += productlist[day][i[0]]['price'] * i[1]
    
    qu = getquerylist("student_to_povar.json")
    qu.append({
        "id": nowid,
        "products": names,
        "name": user['username'],
        "userid": email,
        "time": f'{time_api.time()}',
        "date": f'{request.form.get("date", "Не указано")}'
    })
    setquerylist(name="student_to_povar.json", to=qu)
    admin_qu = getquerylist('student_buys.json')
    admin_qu.append({
        "id": nowid,
        "user": email,
        'class': user['class'],
        'phone': user['phone'],
        "money": sum,
        "what": names,
        "time": f'{time_api.date()}',
        "order_date": f'{time_api.date()}',
        "date": f'{request.form.get("date", "Не указано")}',
        "isCooked": False,
        'isComplete': False
    })
    setquerylist(name="student_buys.json", to=admin_qu)
    user['history'].append({
        "products": names,
        "time": f'{str(datetime.now())[11:16]}',
        "order_date": f'{corr_date(datetime.now().date().day)}.{corr_date(datetime.now().date().month)}.{corr_date(datetime.now().date().year)}',
        "date": f'',
        "money": sum
    })
    user['money'] -= sum
    setuser(email, user)
    return redirect(url_for('clear_cart'))

def payment():
    email = getlogin()
    kwargs = commonkwargs(email)
    if (kwargs['rights'] != 1):
        return redirect(url_for('dashboard'))
    if (request.method == 'POST'):
        photo = request.files['screenshot']
        if (photo.filename != ''):
            photos = getquerylist('payment.json')
            path = f"{base_path}/static/images/screenshots/{len(photos)}.jpg"
            photo.save(path)
            photos.append({
                "approved": 0,
                "email": email,
                "amount": int(request.form.get('money', 0))
            })
            setquerylist(name="payment.json", to=photos)
        return redirect(session.get('previous_page', '/dashboard'))
    return render_template('payment.html', **kwargs)

def pay():
    email = getlogin()
    kwargs = commonkwargs(email)
    if (kwargs['rights'] != 1):
        return redirect(url_for('dashboard'))
    cart_items, cart_total = get_cart_objects(email)
    kwargs['cart_items'] = cart_items
    kwargs['cart_total'] = cart_total
    kwargs['clmonday'] = time_api.closest_monday()
    kwargs['clsaturday'] = time_api.closest_monday(delta = 5)
    return render_template('pay.html', productlist=getproductlist(), takequeries=getuser(email)['to_take'], **kwargs)

def returnback():
    return redirect(session.get('pre_previous_page', '/dashboard'))