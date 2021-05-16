import json
import mysql.connector
import os, datetime
import random
import numpy as np
from content_manager import UseDatabase
import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template,request,redirect, url_for, Blueprint, session
import matplotlib.pyplot as plt

with open('data_files/dbconfig.json', 'r') as f:
	dbconfig = json.load(f)

app = Flask(__name__)
app.config['dbconfig'] = dbconfig

class Coord():
	x = 0
	y = 0

	def __init__(self, x, y):
		self.x = x
		self.y = y

class Element():
	def __init__(self, node1, node2, node3):
		self.node1 = node1
		self.node2 = node2
		self.node3 = node3
		self.count1 = 1
		self.count2 = 1
		self.count3 = 1

	def print_element(self):
		print('(', self.node1.x, ',', self.node1.y, ')', '(', self.node2.x, ',', self.node2.y, ')', '(', self.node3.x, ',', self.node3.y, ')')


def get_data_elements(cursor):
	SQL = f"SELECT id, n1, n2, n3, props FROM elements;"
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['id', 'n1', 'n2', 'n3', 'props']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res

def get_data_nodes(cursor):
	SQL = f"SELECT id, x, y FROM nodes;"
	cursor.execute(SQL)
	result = cursor.fetchall()
	res = []
	schema = ['id', 'x', 'y']
	for blank in result:
		res.append(dict(zip(schema,blank)))
	return res



@app.route('/menu/', methods=['GET','POST'])
def menu_zapros(color, mash, font):
	print(color, mash)
	with UseDatabase(app.config['dbconfig']) as cursor:
		elementsDb = get_data_elements(cursor)
	with UseDatabase(app.config['dbconfig']) as cursor:
		nodesDb = get_data_nodes(cursor)
	elements = []
	for element in elementsDb:
		for node in nodesDb:
			if element['n1'] == node['id']:
				for node2 in nodesDb:
					if element['n2'] == node2['id']:
						for node3 in nodesDb:
							if element['n3'] == node3['id']:
								elem = Element(Coord(node['x'], node['y']), Coord(node2['x'], node2['y']), Coord(node3['x'], node3['y']))
								elements.append(elem)
	for i in range(len(elements) - 1):
		for j in range(i + 1, len(elements)):
			if(elements[i].node1.x == elements[j].node1.x and elements[i].node1.y == elements[j].node1.y or elements[i].node1.x == elements[j].node2.x and elements[i].node1.y == elements[j].node2.y or elements[i].node1.x == elements[j].node3.x and elements[i].node1.y == elements[j].node3.y):
				elements[i].count1 += 1
				if(elements[i].node1.x == elements[j].node1.x and elements[i].node1.y == elements[j].node1.y):
					elements[j].count1 += 1
				if(elements[i].node1.x == elements[j].node2.x and elements[i].node1.y == elements[j].node2.y):
					elements[j].count2 += 1
				if(elements[i].node1.x == elements[j].node3.x and elements[i].node1.y == elements[j].node3.y):
					elements[j].count3 += 1
			if(elements[i].node2.x == elements[j].node2.x and elements[i].node2.y == elements[j].node2.y or elements[i].node2.x == elements[j].node1.x and elements[i].node2.y == elements[j].node1.y or elements[i].node2.x == elements[j].node3.x and elements[i].node2.y == elements[j].node3.y):
				elements[i].count2 += 1
				if(elements[i].node2.x == elements[j].node1.x and elements[i].node2.y == elements[j].node1.y):
					elements[j].count1 += 1
				if(elements[i].node2.x == elements[j].node2.x and elements[i].node2.y == elements[j].node2.y):
					elements[j].count2 += 1
				if(elements[i].node2.x == elements[j].node3.x and elements[i].node2.y == elements[j].node3.y):
					elements[j].count3 += 1
			if(elements[i].node3.x == elements[j].node3.x and elements[i].node3.y == elements[j].node3.y or elements[i].node3.x == elements[j].node1.x and elements[i].node3.y == elements[j].node1.y or elements[i].node3.x == elements[j].node2.x and elements[i].node3.y == elements[j].node2.y):
				elements[i].count3 += 1
				if(elements[i].node3.x == elements[j].node1.x and elements[i].node3.y == elements[j].node1.y):
					elements[j].count1 += 1
				if(elements[i].node3.x == elements[j].node2.x and elements[i].node3.y == elements[j].node2.y):
					elements[j].count2 += 1
				if(elements[i].node3.x == elements[j].node3.x and elements[i].node3.y == elements[j].node3.y):
					elements[j].count3 += 1
	font = {
		'family': 'normal',
		'weight': 'bold',
		'size': int(font)}
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	plt.rc('font', **font)
	for elem in elements:
		x = []
		y = []
		x.append(elem.node1.x)
		x.append(elem.node2.x)
		x.append(elem.node3.x)
		x.append(elem.node1.x)
		y.append(elem.node1.y)
		y.append(elem.node2.y)
		y.append(elem.node3.y)
		y.append(elem.node1.y)
		ax.set_ylim(-100, 100)
		ax.set_xlim(-100, 100)
		ax.plot(x, y, linewidth=2, color=color)
		ax.annotate(f'{elem.count1}', xy=(elem.node1.x + 3, elem.node1.y + 3))
		ax.annotate(f'{elem.count2}', xy=(elem.node2.x + 3, elem.node2.y + 3))
		ax.annotate(f'{elem.count3}', xy=(elem.node3.x + 3, elem.node3.y + 3))
	name = 'plot' + str(random.randint(0,100000)) + '.png'
	plt.savefig('static' + '/' + name, dpi=int(mash))
	return render_template('primer.html', name='/static' + '/' + name)


@app.route('/', methods=['GET','POST'])
def menu():
	if 'send' in request.form and request.form['send']=='Отправить':
		color = request.form.get('color')
		mash = request.form.get('mashtab')
		font = request.form.get('font')
		if(color != 'yellow' and color != 'red' and color != 'green' and color != 'black'):
			return render_template('main.html')
		return menu_zapros(color, mash, font) 	
	else:
		return render_template('main.html')

app.run(debug = True)