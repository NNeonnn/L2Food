from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_session import Session
from subscript.filework import *
from subscript.account_system import *
import subscript.simple_routes as simple_r
import subscript.account_routes as account_r
import subscript.student_routes as student_r
import subscript.admin_routes as admin_r
import subscript.time_api as time_api
import os
import secrets
from datetime import datetime

#Configs
app = Flask(__name__)
app.secret_key = secrets.token_hex(36)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = SESSION_PATH
app.config['SESSION_PERMANENT'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
Session(app)

#simple_routes.py
app.add_url_rule('/', view_func=simple_r.landing)
#account_routes.py
app.add_url_rule('/login', view_func=account_r.login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=account_r.register, methods=['GET', 'POST'])
app.add_url_rule('/confirm_mail', view_func=account_r.confirm_mail, methods=['GET', 'POST'])
app.add_url_rule('/profile', view_func=account_r.profile, methods=['GET', 'POST'])
app.add_url_rule('/login_wout_pass', view_func=account_r.login_wout_pass, methods=['GET', 'POST'])
app.add_url_rule('/confirm_login_mail', view_func=account_r.confirm_login_mail, methods=['GET', 'POST'])
app.add_url_rule('/choose', view_func=account_r.choose)
#student_routes.py
app.add_url_rule('/add_to_cart', view_func=student_r.add_to_cart, methods=['GET'])
app.add_url_rule('/clear_cart', view_func=student_r.clear_cart)
app.add_url_rule('/buy_from_cart', view_func=student_r.buy_from_cart, methods=['POST'])
app.add_url_rule('/remove_from_cart', view_func=student_r.remove_from_cart, methods=['GET'])
app.add_url_rule('/payment', view_func=student_r.payment, methods=['GET', 'POST'])
app.add_url_rule('/pay', view_func=student_r.pay, methods=['GET'])
app.add_url_rule('/returnback', view_func=student_r.returnback)
#admin_routes.py
app.add_url_rule('/download_student_report', view_func=admin_r.download_student_report)
app.add_url_rule('/download_product_report', view_func=admin_r.download_product_report)
app.add_url_rule('/approve_balance_req/<id>', view_func=admin_r.approve_balance_req)
app.add_url_rule('/decline_balance_req/<id>', view_func=admin_r.decline_balance_req)
app.add_url_rule('/download_receipt/<receipt_id>', view_func=admin_r.download_receipt)
app.add_url_rule('/remove_from_modal/<int:day>&<int:id>', view_func=admin_r.remove_from_modal)
app.add_url_rule('/add_to_modal/<int:day>&<int:id>', view_func=admin_r.remove_from_modal)

#@app.errorhandler(404)
#def four04(error):
#    return render_template('404.html', **commonkwargs(getlogin(reset_auth=False)))

#@app.errorhandler(Exception)
#def fatal_error(error):
#    return render_template('404.html', **commonkwargs(getlogin(reset_auth=False)))

@app.before_request
def store_current_page():
    if request.endpoint and request.method == 'GET' and request.endpoint != 'static':
        if (session.get('now_page', '/') != request.url):
            session['previous_page'] = session.get('now_page', '/dashboard')
            session['now_page'] = request.url

@app.route('/dashboard')
def dashboard():
    user = User()
    if (not user.exists()):
        return render_template('dashboard.html', productlist=getproductlist(), **user.kwargs())
    elif (user.data['rights'] == 1):
        cart_items, cart_total = student_r.get_cart_objects(user)
        kwargs = user.kwargs()
        kwargs['cart_items'] = cart_items
        kwargs['cart_total'] = cart_total
        kwargs['clmonday'] = time_api.closest_monday()
        kwargs['clsaturday'] = time_api.closest_monday(delta = 5)
        return render_template('dashboard.html', productlist=getproductlist(), takequeries=user.data['to_take'], **kwargs)
    elif (user.data['rights'] == 2):
        balance_q = getquerylist('payment.json')
        balance_requests = []
        for i in balance_q:
            us = getuser(i['email'])
            balance_requests.append({
                "approved": i['approved'],
                "email": i['email'],
                "name": us['username'],
                "amount": i['amount'],
                "phone": us['phone'],
                "grade": us['class']
            })
        return render_template('dashboard.html', **user.kwargs(), balance_requests=balance_requests, productlist=getproductlist(), globalproductlist=getglobalproductlist())

#start
if __name__ == '__main__':
    app.run(port=5237, host="127.0.0.1", debug=True)