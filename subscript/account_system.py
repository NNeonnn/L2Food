#Выделенный файл для работы с аккаунтами

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import session
from subscript.filework import does_user_exist, getuser, setuser, return_image

Debug_mode = True #эта переменная при состоянии True вместо отправки кода на почту выводит его в print()
                   #вызвано тем, что слишком много писем с mail.ru почты приводит к блокировке почты из-за спама
                   #(может уже нет, так как я написал в поддержку, но это не факт)

class User:
    def __init__(self, email = '', reset_auth = True):
        if email != '':
            self.__mail = email
            self.data = getuser(email)
            reset_auth = False
        if session.get('user', '') == '':
            session['user'] = 'placeholder'
            self.__mail = 'placeholder'
            self.data = {}
        if (reset_auth):
            session['auth'] = False
        if (not does_user_exist(session.get('user', ''))):
            session['user'] = 'placeholder'
            self.__mail = 'placeholder'
            self.data = {}

    def exists(self):
        ans = does_user_exist(self.__mail)
        if (ans == False):
            self.__mail = 'placeholder'
            self.data = {}
        return ans
    
    def set(self, email):
        if does_user_exist(session.get(email, 'placeholder')):
            session['user'] = email
            self.__mail = email
            self.data = getuser(email)
        else:
            session['user'] = 'placeholder'
            self.__mail = 'placeholder'
            self.data = {}

    def commit(self):
        if (self.__mail != 'placeholder'):
            setuser(self.__mail, self.data)
    
    @property
    def mail(self):
        return self.__mail
    
    def kwargs(self):
        if (self.exists()):
            ans = dict()
            ans['userimg'] = return_image(f'users/{self.__mail}', 'user_placeholder')
            for u in self.data:
                if (u != 'password'):
                    ans[u] = self.data[u]
            return ans
        else:
            return {'username': 'Log in', 'userimg': return_image(f'users/{self.__mail}', 'user_placeholder'), \
                'description': 'empty', 'phone': 'N/A', 'class': 'N/A', 'class_grade': 1, 'class_letter': 'A', \
                'rights': 0, 'money': 0, 'abonement': 'null'}

class Student(User):
    def exists(self):
        ans = does_user_exist(self.__mail)
        if (ans == False):
            self.__mail = 'placeholder'
            self.data = {}
        if (self.data(self.__mail).get('rights', 2) == 2):
            self.__mail = 'placeholder'
            self.data = {}
            ans = False
        return ans

class Admin(User):
    def exists(self):
        ans = does_user_exist(self.__mail)
        if (ans == False):
            self.__mail = 'placeholder'
            self.data = {}
        if (self.data(self.__mail).get('rights', 1) == 1):
            self.__mail = 'placeholder'
            self.data = {}
            ans = False
        return ans

def getlogin(reset_auth = True):
    if session.get('user', '') == '':
        session['user'] = 'placeholder'
    if (reset_auth):
        session['auth'] = False
    if (not does_user_exist(session.get('user', ''))):
        session['user'] = 'placeholder'
    return session['user']

def setlogin(email):
    session['user'] = email

def sendmail(mail, code):
    if (Debug_mode):
        print(f"Ваш код: {code}")
        return
    fromaddr = "PASTE_EMAIL_HERE"
    toaddr = mail
    mypass = "PASTE_PASS_HERE"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Ваш код авторизации"
    scode = ""
    for i in code:
        scode += str(i)
    body = f"Ваш код: {code}"
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465) # PASTE SERVER SSL HERE
    server.login(fromaddr, mypass)
    text = msg.as_string()
    try:
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    except:
        server.quit()