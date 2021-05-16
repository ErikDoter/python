import json
import mysql.connector
from functools import wraps
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session

with open('data_files/access.json', 'r') as f:
	access = json.load(f)

backet = Blueprint('backet_bp', __name__, template_folder = 'templates', static_folder = 'static')

def login_required(func):
	@wraps(func)
	def wrapper():
		if (session['user_group'] in access['backet']):
			return func()
		elif session['user_group'] != "guest":
			return redirect('/menu')
		else:
			print(session['user_group'])
			return redirect('/login')
	return wrapper


@backet.route('/', methods=['GET','POST'])
@login_required
def catalog():
	if 'send' in request.form and request.form['send']=='Добавить':
		choice_id = request.form.get('id')
		choice_name = request.form.get('name')
		count = request.form.get('count')
		if check_is(choice_id) == 0:
			put_into_basket(count, choice_id, choice_name)
		with UseDatabase(current_app.config['dbconfig']) as cursor:
			catalog = get_catalog(cursor)
			return render_template('backet/catalog.html', catalog = catalog, len = session['basket_len'])
	elif 'send' in request.form and request.form['send']=='Показать план':
		backet = get_backet()
		return render_template('backet/backet.html', backet = backet)
	elif 'send' in request.form and request.form['send']=='Вернуться':
		with UseDatabase(current_app.config['dbconfig']) as cursor:
			catalog = get_catalog(cursor)
			return render_template('backet/catalog.html', catalog = catalog, len = session['basket_len'])
	elif 'send' in request.form and request.form['send']=='Очистить':
		delete_from_backet()
		return redirect('/catalog')
	elif 'send' in request.form and request.form['send']=='Подтвердить':
		with UseDatabase(current_app.config['dbconfig']) as cursor:
			save_basket(cursor)
			delete_from_backet()
			return render_template('backet/end.html')
	elif 'send' in request.form and request.form['send'] == 'Показать вариативные дисциплины':
		with UseDatabase(current_app.config['dbconfig']) as cursor:
			catalog = get_catalog(cursor)
			return render_template('backet/catalog.html', catalog = catalog)
	elif 'send' in request.form and request.form['send'] == 'Дальше':
		session['student'] = [request.form.get('student'), request.form.get('semestr')]
		with UseDatabase(current_app.config['dbconfig']) as cursor:
			catalog = get_important(cursor)
			return render_template('backet/important.html', catalog = catalog)
	elif 'send' in request.form and request.form['send'] == 'Убрать':
		session['cart'] = delete_one_backet(request.form.get('id'))
		return render_template('backet/backet.html', backet = session['cart'])
	else:
		return render_template('backet/who.html')



def get_catalog(cursor):
	SQL = f"""SELECT d_id, name, total_hours
	FROM discipline where vriability = 1"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	schema = ['id', 'name', 'total_hours']
	res = []
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res

def get_important(cursor):
	SQL = f"""SELECT d_id, name, total_hours
	FROM discipline where vriability = 0"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	schema = ['id', 'name', 'total_hours']
	res = []
	for blank in result:
		res.append(dict(zip(schema,blank)))
	print(res)
	return res

def put_into_basket(quantity,choice_id,choice_name):
	 choice_item = {
		'choice_id' : int(choice_id),
		'choice_name' : choice_name,
		'quantity' : int(quantity),
	 }
	 session['cart'].append(choice_item)
	 session['basket_len'] += 1
	 return session['basket_len']


def get_backet():
	backet = session['cart']
	return backet

def delete_from_backet():
	session['cart'] = []
	session['basket_len'] = 0
	pass

def delete_one_backet(id):
	index = 0
	for i in range(len(session['cart'])):
		if int(session['cart'][i]['choice_id']) == int(id):
			index = i
	session['cart'].pop(index)
	session['basket_len'] -= 1
	return session['cart']

def check_is(id):
	for element in session['cart']:
		if int(element['choice_id']) == int(id):
			return 1
	return 0

def save_basket(cursor):
	basket_len = len(session['cart'])
	_SQLIn = """insert into academic_plan values(NULL, %s, 0, %s, %s)"""
	_SQLSEL = """select ap_id from academic_plan where semestr = %s and s_fk = %s"""
	cursor.execute(_SQLIn, (session['student'][1], basket_len, session['student'][0]))
	cursor.execute(_SQLSEL, (session['student'][1], session['student'][0]))
	result = cursor.fetchall()
	res = []
	schema = ['id']
	for blank in result:
		res.append(dict(zip(schema,blank)))

	_SQL = """insert into ap_d values(NULL,%s,%s)"""
	for i in range(basket_len):
		values = session['cart'][i].values()
		values = list(values)
		cursor.execute(_SQL,(res[0]['id'], values[0]))
	pass