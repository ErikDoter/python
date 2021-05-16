import json
import mysql.connector
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session

login = Blueprint('login_bp', __name__, template_folder = 'templates', static_folder = 'static')

@login.route('/', methods=['GET','POST'])
def auth():
	if 'send' in request.form and request.form['send']=='Отправить':
		login = request.form.get('login')
		password = request.form.get('password')
		if password and login:
			with UseDatabase(current_app.config['dbconfig']) as cursor:
				db = check(cursor, login, password)
				print("aaa")
				print(current_app.config['dbconfig'].items())
				current_app.config['dbconfig']['user'] = db['login']
				current_app.config['dbconfig']['password'] = db['password']
				session['user_group'] = db['g_name']
				print("qqqqqqqqqqq", current_app.config['dbconfig'].items())
				return redirect('/menu')
		else:
			return render_template('login/entry.html')
	else:
			return render_template('login/entry.html')
	

def check(cursor, login, password):
	SQL = f"""SELECT g.login, g.password, g.g_name 
	FROM my_user u JOIN my_group g ON (u.g_name = g.g_name) 
	WHERE u.login = '{login}' and u.password = '{password}';"""
	cursor.execute(SQL)
	result = cursor.fetchall()
	schema = ['login', 'password', 'g_name']
	for blank in result:
		res = dict(zip(schema,blank))
	return res

