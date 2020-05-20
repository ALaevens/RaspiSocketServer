import sqlite3

def openDB(dbFilename):
	conn = None
	try:
		conn = sqlite3.connect(dbFilename)
	except Exception as e:
		print(e)

	return conn

def queryConnectionCount(conn, addr):
	cur = conn.cursor()
	cur.execute("SELECT count FROM connections WHERE address = (?)", (addr,))
	row = cur.fetchone()

	if row != None:
		return row[0]
	else:
		return 0

def updateConnections(addr):
	conn = openDB("/home/alex/socket/connections.db")

	count = queryConnectionCount(conn, addr)

	cur = conn.cursor()

	SQL = ""
	if count == 0:
		SQL = 'INSERT INTO connections VALUES ((?), 1)'
	else:
		SQL = 'UPDATE connections SET count = count + 1 WHERE address = (?)'

	cur.execute(SQL, (addr,))
	conn.commit()
	conn.close()

	return count + 1
