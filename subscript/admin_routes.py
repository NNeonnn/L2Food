#Выделенный файл для всех путей, связанных со страницей товаров

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *
from subscript.reports import *

def remove_from_modal(day):
    day = int(day)
    id = request.args.get('id', default=-1, type=int)
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('dashboard'), 302)
    user_data = getuser(email)
    if not user_data or user_data.get('rights', 0) < 2:
        return redirect(url_for('dashboard'), 302)
    modal = getproductlist()
    modal[day].pop(str(id))
    setproductlist(modal)
    return redirect(url_for('dashboard'), 302)

def download_receipt(receipt_id):
    """
    Отдаёт файл чека по ID запроса.
    Сначала ищет .jpg, потом .pdf в static/images/screenshots/
    """
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'))

    # Только админ или оператор может скачивать
    user_data = getuser(email)
    if not user_data or user_data.get('rights', 0) < 2:
        return redirect(url_for('dashboard'))

    base_dir = os.path.join('static', 'images', 'screenshots')
    # пробуем оба расширения
    for ext in ['jpg', 'pdf']:
        file_path = os.path.join(base_dir, f'{receipt_id}.{ext}')
        if os.path.isfile(file_path):
            # определяем MIME
            mimetype = 'image/jpeg' if ext == 'jpg' else 'application/pdf'
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f'чек_{receipt_id}.{ext}',
                mimetype=mimetype
            )

    # Если ничего не найдено – отдаём заглушку или 404
    return "Файл не найден", 404

def download_student_report():
    """
    Маршрут для скачивания отчета по пользователям
    """
    # Проверяем авторизацию
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('dashboard'), 302)
    
    # Проверяем права (только администраторы могут скачивать отчеты)
    user_data = getuser(email)
    if not user_data or user_data.get('rights', 0) < 2:
        return redirect(url_for('dashboard'), 302)
    
    # Генерируем отчет
    users_dir = f'{base_path}/queries/student_buys.json'
    excel_file = generate_student_buys_report(users_dir)
    
    # Создаем имя файла с текущей датой и временем
    filename = f"отчет_заказы_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
    
    # Отправляем файл
    return send_file(
        excel_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def download_product_report():
    """
    Маршрут для скачивания отчета по пользователям
    """
    # Проверяем авторизацию
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('dashboard'), 302)
    
    # Проверяем права (только администраторы могут скачивать отчеты)
    user_data = getuser(email)
    if not user_data or user_data.get('rights', 0) < 2:
        return redirect(url_for('dashboard'), 302)
    
    # Генерируем отчет
    users_dir = f'{base_path}/queries/povar_to_admin.json'
    excel_file = generate_product_report(users_dir)
    
    # Создаем имя файла с текущей датой и временем
    filename = f"отчет_продукты_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
    
    # Отправляем файл
    return send_file(
        excel_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def approve_balance_req(id):
    email = getlogin()
    user = getuser(email)
    if email == 'placeholder' or user['rights'] != 2:
        return redirect(url_for('login'))
    qu = getquerylist("payment.json")
    id = int(id)
    if (id < len(qu)):
        qu[id]['approved'] = 1
        us = getuser(qu[id]['email'])
        us['money'] += qu[id]['amount']
        setuser(qu[id]['email'], us)
    setquerylist(name="payment.json", to=qu)
    return redirect(url_for('c'), 302)

def decline_balance_req(id):
    email = getlogin()
    user = getuser(email)
    if email == 'placeholder' or user['rights'] != 2:
        return redirect(url_for('login'))
    qu = getquerylist("payment.json")
    id = int(id)
    if (id < len(qu)):
        qu[id]['approved'] = -1
    setquerylist(name="payment.json", to=qu)
    return redirect(url_for('dashboard'), 302)