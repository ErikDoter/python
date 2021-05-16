import mysql.connector
import json

class UseDatabase:

	def __init__(self, dbconfig):
		self.configuration = dbconfig

	def __enter__(self):
		self.conn = mysql.connector.connect(**self.configuration)
		self.cursor = self.conn.cursor()
		return self.cursor

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.conn.commit()
		self.cursor.close()
		self.conn.close()