#Выделенный файл для всех путей, связанных с аккаунтами

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *
from subscript.password_hashing import *
from random import randint

def choose():
    user = User()
    if (not user.exists()):
        return render_template('choose.html', **user.kwargs())
    else:
        return redirect(url_for('profile'), 302)

def login():
    user = User()
    if (user.exists()):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        if len(data['email']) > 0 and len(data['password']) > 0:
            input_email = data['email'][0]
            input_password = data['password'][0]
            if getuser(input_email) != False and verify_password(User(email=data['email'][0]).data['password'], input_password):
                user.set(input_email)
                return redirect(url_for('profile'), 302)
            else:
                return render_template('login.html', wrong=True, **user.kwargs())
        else:
            return render_template('login.html', wrong=True, **user.kwargs())
    return render_template('login.html', wrong=False, **user.kwargs())

def register():
    user = User()
    if (user.exists()):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        session['temp_email'] = data['email'][0]
        session['temp_password'] = hash_password(data['password'][0])
        session['temp_last_name'] = data.get('last_name', [''])[0].strip()
        session['temp_first_name'] = data.get('first_name', [''])[0].strip()
        session['temp_middle_name'] = data.get('middle_name', [''])[0].strip()
        session['temp_name'] = f"{session['temp_last_name']} {session['temp_first_name']} {session['temp_middle_name']}".strip()
        session['temp_rights'] = data['rights'][0]
        session['auth'] = True
        return redirect(url_for('confirm_mail'), 302)
    return render_template('register.html', **user.kwargs())

def confirm_mail():
    user = User(reset_auth = False)
    if (user.exists() or session['auth'] == False):
        return redirect(url_for('profile'), 302)
    if (request.method == 'GET'):
        code = []
        scode = ""
        for i in range(4):
            code.append(randint(0, 9))
            scode += str(code[i])
        session['auth_code'] = code
        if (Debug_mode):
            print(f'Ваш код: {scode}')
        else:
            sendmail(session['temp_email'], scode)
        return render_template('confirm_mail.html', **user.kwargs(), redirectto='confirm_mail')
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        for i in range(4):
            if session['auth_code'][i] != int(data[f'code{i}'][0]):
                return redirect(url_for('confirm_mail'), 302)
        setuser(session['temp_email'], {})
        user.set(session['temp_email'])
        user.data = {
            'password': session['temp_password'],
            'username': session.get('temp_name', ''),
            'last_name': session.get('temp_last_name', ''),
            'first_name': session.get('temp_first_name', ''),
            'middle_name': session.get('temp_middle_name', ''),
            'money': 0,
            'class': "",
            'description': "",
            'phone': "",
            'rights': int(session['temp_rights']),
            'cart': [[], [], [], [], [], []],
            'history': []
        }
        user.commit()
        session['temp_password'] = ""
        return redirect(url_for('profile'), 302)
    return redirect(url_for('register'), 302)

def login_wout_pass():
    user = User()
    if (user.exists()):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        input_email = data['email'][0]
        if len(data['email']) > 0 and User(email=data['email'][0]).exists():
            session['temp_mail'] = input_email
            session['auth'] = True
            return redirect(url_for('confirm_login_mail'), 302)
        else:
            return render_template('login_wout_pass.html', wrong=True, **user.kwargs())
    return render_template('login_wout_pass.html', wrong=False, **user.kwargs())

def confirm_login_mail():
    user = User(reset_auth=False)
    if (user.exists() or session['auth'] == False):
        return redirect(url_for('profile'), 302)
    if (request.method == 'GET'):
        code = []
        scode = ""
        for i in range(4):
            code.append(randint(0, 9))
            scode += str(code[i])
        session['auth_code'] = code
        sendmail(session['temp_mail'], scode)
        return render_template('confirm_mail.html', **user.kwargs(), redirectto='confirm_login_mail')
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        for i in range(4):
            if session['auth_code'][i] != int(data[f'code{i}'][0]):
                return redirect(url_for('confirm_login_mail'), 302)
        user.set(session['temp_mail'])
        return redirect(url_for('profile'), 302)
    return redirect(url_for('register'), 302)

def profile():
    user = User()
    if (not user.exists()):
        return redirect(url_for('login'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict()
        # Выход
        if (data['commit_type'] == 'logout'):
            user.set('')
            return redirect(url_for('landing'), 302)
        # Обновление информации
        if (data['commit_type'] == 'update_data'):
            changes = user.data
            for i in data:
                if len(data[i]) > 0:
                    changes[i] = data[i].strip()
            # ФИО
            if 'last_name' in data and len(data['last_name']) > 0:
                changes['last_name'] = data['last_name'].strip()
            if 'first_name' in data and len(data['first_name']) > 0:
                changes['first_name'] = data['first_name'].strip()
            if 'middle_name' in data and len(data['middle_name']) > 0:
                changes['middle_name'] = data['middle_name'].strip()
            # Полный ФИО
            changes['username'] = f"{changes.get('last_name', '')} {changes.get('first_name', '')} {changes.get('middle_name', '')}".strip()
            # Собирать класс человека
            changes['class'] = f"{changes.get('class_grade', '')}{changes.get('class_letter', '')}".strip()
            for i in changes:
                user.data[i] = changes[i]
            user.commit()
        # Фото
        if (data['commit_type'] == 'update_photo'):
            if (request.files['avatar'].filename == ''):
                if (os.path.exists(f"{base_path}/static/images/users/{user.mail}.jpg")):
                    os.remove(f"{base_path}/static/images/users/{user.mail}.jpg")
            else:
                photo = request.files['avatar']
                if (photo.filename != ''):
                    path = f"{base_path}/static/images/users/{user.mail}.jpg"
                    photo.save(path)
    show_corr = False
    if request.method == 'POST':
        show_corr = True
    return render_template('profile.html', **user.kwargs(), show_corr=show_corr)
