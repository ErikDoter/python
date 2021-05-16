import json
import mysql.connector
from functools import wraps
from content_manager import UseDatabase
from flask import Flask, render_template,request,redirect, url_for, Blueprint, current_app, session


zapros1 = Blueprint('zapros1', __name__, template_folder = 'templates', static_folder = 'static')

with open('data_files/access.json', 'r') as f:
	access = json.load(f)

def login_required(func):
	@wraps(func)
	def wrapper():
		if (session['user_group'] in access['requests']):
			return func()
		else:
			print(session['user_group'])
			return redirect('/login')
	return wrapper

@zapros1.route('/', methods=['GET','POST'])
@login_required
def index():
	if 'send' in request.form and request.form['send']=='Отправить':
		month = request.form.get('month')
		year = request.form.get('year')
		if month and year:
			with UseDatabase(current_app.config['dbconfig']) as cursor:
				otchet = form_otchet(cursor, month, year)
			return render_template('zapros1/zapros1.html', month = month, year = year, otchet = otchet)
		else:
			return render_template('zapros1/entry.html')
	elif 'send' in request.form and request.form['send']=='Отправить(2)':
		subject = request.form.get('zapros2')
		if subject:
			with UseDatabase(current_app.config['dbconfig']) as cursor:
				otchet = zapros2(cursor, subject)
				print("zapros2", otchet)
			return render_template('zapros1/zapros2.html', subject = subject, otchet = otchet)
		else: 
			return redirect('/zapros1')
	elif 'send' in request.form and request.form['send']=='Отправить(3)':
		with UseDatabase(current_app.config['dbconfig']) as cursor:
			otchet = zapros3(cursor)
			print(otchet)
		return render_template('zapros1/zapros3.html', otchet = otchet)
	elif 'send' in request.form and request.form['send']=='Отправить(4)':
		with UseDatabase(current_app.config['dbconfig']) as cursor:
			otchet = zapros4(cursor)
			print(otchet)
		return render_template('zapros1/zapros4.html', otchet = otchet)
	elif 'send' in request.form and request.form['send']=='Отправить(5)':
		with UseDatabase(current_app.config['dbconfig']) as cursor:
			otchet = zapros5(cursor)
			print(otchet)
		return render_template('zapros1/zapros5.html', otchet = otchet)
	elif 'send' in request.form and request.form['send']=='Отправить(6)':
		year = request.form.get('zapros6_year')
		if year:
			with UseDatabase(current_app.config['dbconfig']) as cursor:
				otchet = zapros6(cursor, year)
				print(otchet)
			return render_template('zapros1/zapros6.html', year = year, otchet = otchet)
		else: 
			return redirect('/zapros1')				
	else:
			return render_template('zapros1/entry.html')
	


def form_otchet(cursor, month, year):
	SQL = f"SELECT d_id, name, total_labs, total_sems, total_hours, total_lec, vriability FROM discipline d left join ap_d a on d.d_id = a.d_fk left join academic_plan ap on ap.ap_id = a.ap_fk where apd_id not in (select distinct ap_id from academic_plan where year(year_plan)= {year}) and vriability=1 group by name;"
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['d_id', 'name', 'total_labs', 'total_sems', 'total_hours', 'total_lec', 'vriability']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res

def zapros2(cursor, subject):
	SQL = f"SELECT speciality, count(*) FROM ap_d a join discipline d on d.d_id = a.d_fk join academic_plan ap on ap.ap_id = a.ap_fk join student s on s.s_id=ap.s_fk where name='{subject}' group by speciality;"
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['speciality', 'count']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res

def zapros3(cursor):
	SQL = f"SELECT * FROM `discipline` Where total_hours = (SELECT MAX(total_hours) FROM discipline);"
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['d_id', 'name', 'total_labs', 'total_sems', 'total_hours', 'total_lec', 'vriability']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res

def zapros4(cursor):
	SQL = f"SELECT ap_id, semestr, year_plan, min_var_discipline FROM ap_d a join discipline d on d.d_id = a.d_fk join academic_plan ap on ap.ap_id = a.ap_fk Where vriability=1 group by ap_id order by count(*) DESC LIMIT 1;"
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['ap_id', 'semestr', 'year_plan', 'min_var_discipline']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res

def zapros5(cursor):
	SQL = f"SELECT d_id, name, total_labs, total_sems, total_hours, total_lec, vriability FROM discipline d left join ap_d a on d.d_id = a.d_fk where apd_id is NULL and vriability=1; "
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['d_id', 'name', 'total_labs', 'total_sems', 'total_hours', 'total_lec', 'vriability']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res

def zapros6(cursor, year):
	SQL = f"SELECT d_id, name, total_labs, total_sems, total_hours, total_lec, vriability FROM discipline d left join ap_d a on d.d_id = a.d_fk left join academic_plan ap on ap.ap_id = a.ap_fk where apd_id not in (select distinct ap_id from academic_plan where year(year_plan)= {year}) and vriability=1 group by name; "
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['d_id', 'name', 'total_labs', 'total_sems', 'total_hours', 'total_lec', 'vriability']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res
