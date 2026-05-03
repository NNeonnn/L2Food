#Выделенный файл для всех путей, связанных с учениками (корзина, получение заказов, оплата)

from flask import render_template, request, redirect, url_for, send_file, session, render_template_string
from subscript.filework import *
from subscript.account_system import *
import subscript.time_api as time_api
from datetime import datetime

def get_cart_objects(user: User):
    if not user.exists():
        return [[], [], [], [], [], []], 0
    cart_ids = user.data['cart']
    all_products = ModalProductlist()
    cart_items = [[], [], [], [], [], []]
    total_price = 0
    for day in range(6):
        for item_id in cart_ids[day]:
            item = all_products.get_one(day, item_id[0])
            cart_items[day].append([item, item_id[1]])
            total_price += item['price'] * item_id[1]
    return cart_items, total_price

def add_to_cart():
    user = Student()
    if not user.exists():
        return redirect(url_for('login'))
    day = int(request.args.get('day', default = -1))
    id = int(request.args.get('id', default = -1))
    if day == -1 or id == -1:
        return redirect(url_for('dashboard'))
    for i in range(len(user.data['cart'][day])):
        if (user.data['cart'][day][i][0] == id):
            user.data['cart'][day][i][1] += 1
            user.commit()
            return redirect(url_for('dashboard'))
    user.data['cart'][day].append([int(id), 1])
    user.commit()
    return redirect(url_for('dashboard'))

def remove_from_cart():
    user = Student()
    if not user.exists():
        return redirect(url_for('login'))
    day = int(request.args.get('day', default = -1))
    id = int(request.args.get('id', default = -1))
    if day == -1 or id == -1:
        return redirect(url_for('dashboard'))
    for i in range(len(user.data['cart'][day])):
        if (user.data['cart'][day][i][0] == id):
            user.data['cart'][day][i][1] -= 1
            if user.data['cart'][day][i][1] == 0:
                user.data['cart'][day].remove(user.data['cart'][day][i])
            user.commit()
            return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

def clear_cart():
    user = Student()
    if user.exists():
        user.data['cart'] = [[], [], [], [], [], []]
        user.commit()
    return redirect(url_for('dashboard'))

def buy_from_cart():
    user = Student()
    if not user.exists():
        return redirect(url_for('login'))
    obj, sum = get_cart_objects(user)
    if (user.data['money'] < sum):
        return redirect(url_for('pay'))
    productlist = ModalProductlist()
    names = [[], [], [], [], [], []]
    for day in range(6):
        for i in user.data['cart'][day]:
            if (i[1] == 1):
                names[day].append(productlist.get_one(day, i[0])['name'])
            else:
                names[day].append(f"{productlist.get_one(day, i[0])['name']} x{i[1]}")
    for day in range(6):
        for i, cnt in user.data['cart'][day]:
            UserQueries().insert(day, user.mail, i, cnt)
    user.data['history'].append({
        "products": names,
        "time": f'{str(datetime.now())[11:16]}',
        "order_date": f'{time_api.date()}',
        "date": f'{time_api.closest_monday()} - {time_api.closest_monday(delta=5)}',
        "money": sum
    })
    user.data['money'] -= sum
    user.commit()
    return redirect(url_for('clear_cart'))

def payment():
    user = Student()
    if not user.exists():
        return redirect(url_for('dashboard'))
    if (request.method == 'POST'):
        photo = request.files['screenshot']
        if (photo.filename != ''):
            print(f"{base_path}/static/images/screenshots/{PaymentQueries().count()}.jpg")
            PaymentQueries().insert(user.mail, int(request.form.get('money', 0)))
            path = f"{base_path}/static/images/screenshots/{PaymentQueries().count()}.jpg"
            photo.save(path)
        return redirect(session.get('previous_page', '/dashboard'))
    return render_template('payment.html', **user.kwargs())

def pay():
    user = Student()
    if not user.exists():
        return redirect(url_for('dashboard'))
    cart_items, cart_total = get_cart_objects(user)
    kwargs = user.kwargs()
    kwargs['cart_items'] = cart_items
    kwargs['cart_total'] = cart_total
    kwargs['clmonday'] = time_api.closest_monday()
    kwargs['clsaturday'] = time_api.closest_monday(delta = 5)
    return render_template('pay.html', productlist=ModalProductlist().get_all(), **kwargs)

def returnback():
    return redirect(session.get('previous_page', '/dashboard'))