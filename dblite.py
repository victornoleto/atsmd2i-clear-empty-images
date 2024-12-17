import sqlite3

DATABASE_NAME = 'database.sqlite'

def get_conn():
	return sqlite3.connect(DATABASE_NAME)

def insert(tablename, data):

	conn = get_conn()
	cursor = conn.cursor()

	columns = ', '.join(data.keys())
	placeholders = ', '.join('?' * len(data))
	values = tuple(data.values())

	cursor.execute(f'INSERT INTO {tablename} ({columns}) VALUES ({placeholders})', values)

	conn.commit()
	conn.close()

def get(tablename):
	
	return exec_select(f'SELECT * FROM {tablename}')

def exec_select(query):

	conn = get_conn()
	cursor = conn.cursor()

	cursor.execute(query)
	rows = cursor.fetchall()

	columns = [column[0] for column in cursor.description]

	conn.close()

	return [
		dict(zip(columns, row)) for row in rows
	]

def init():

	conn = get_conn()
	cursor = conn.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS history (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			path TEXT NOT NULL,
			kb INTEGER NOT NULL,
			pass_id INTEGER,
			created_at TIMESTAMP DEFAULT CURRENT
		)
	''')

	conn.commit()
	conn.close()