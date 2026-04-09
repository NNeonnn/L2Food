#Выделенный файл для всех путей, связанных со страницей товаров

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *

def product_detail(id):
    product_data = getproduct(id)
    if not product_data:
        return render_template('404.html', **commonkwargs(getlogin()))
    return render_template('product.html', id=id, product=product_data, **commonkwargs(getlogin()))