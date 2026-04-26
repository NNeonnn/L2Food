#Выделенный файл для всех путей, связанных со страницей товаров

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *
from subscript.reports import *

def remove_from_modal(day, id):
    user = Admin()
    if not user.exists():
        return redirect(url_for('dashboard'), 302)
    modal = getproductlist()
    modal[day].pop(str(id))
    setproductlist(modal)
    return redirect(url_for('dashboard'), 302)

def add_to_modal(day, id):
    return redirect(url_for('dashboard'), 302)

def download_receipt(receipt_id):
    user = Admin()
    if not user.exists():
        return redirect(url_for('dashboard'), 302)
    base_dir = os.path.join('static', 'images', 'screenshots')
    for ext in ['jpg', 'pdf']:
        file_path = os.path.join(base_dir, f'{receipt_id}.{ext}')
        if os.path.isfile(file_path):
            mimetype = 'image/jpeg' if ext == 'jpg' else 'application/pdf'
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f'чек_{receipt_id}.{ext}',
                mimetype=mimetype
            )
    return redirect(url_for('dashboard'), 302)

def download_student_report():
    user = Admin()
    if not user.exists():
        return redirect(url_for('dashboard'), 302)
    users_dir = f'{base_path}/queries/student_buys.json'
    excel_file = generate_student_buys_report(users_dir)
    filename = f"отчет_заказы_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
    return send_file(
        excel_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def approve_balance_req(id):
    user = Admin()
    if not user.exists():
        return redirect(url_for('dashboard'), 302)
    qu = getquerylist("payment.json")
    id = int(id)
    if (id < len(qu)):
        qu[id]['approved'] = 1
        us = getuser(qu[id]['email'])
        us['money'] += qu[id]['amount']
        setuser(qu[id]['email'], us)
    setquerylist(name="payment.json", to=qu)
    return redirect(url_for('dashboard'), 302)

def decline_balance_req(id):
    user = Admin()
    if not user.exists():
        return redirect(url_for('dashboard'), 302)
    qu = getquerylist("payment.json")
    id = int(id)
    if (id < len(qu)):
        qu[id]['approved'] = -1
    setquerylist(name="payment.json", to=qu)
    return redirect(url_for('dashboard'), 302)