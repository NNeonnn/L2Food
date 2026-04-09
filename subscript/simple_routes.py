#Выделенный файл для однострочных функций путей

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *

def landing():
    return render_template('landing.html', **commonkwargs(getlogin()))