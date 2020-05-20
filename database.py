import sqlite3
import ipinfo
import ipaddress

def openDB(dbFilename):
	conn = None
	try:
		conn = sqlite3.connect(dbFilename)
	except Exception as e:
		print(e)

	return conn

def queryConnectionCount(conn, addr):
	cur = conn.cursor()
	cur.execute("SELECT count FROM addresses WHERE address = (?)", (addr,))
	row = cur.fetchone()

	if row != None:
		return row[0]
	else:
		return 0

def queryConnectionCountry(conn, addr):
	cur = conn.cursor()
	cur.execute("SELECT country FROM addresses WHERE address = (?)", (addr,))
	row = cur.fetchone()
	if row != None:
		return row[0]
	else:
		return "Unknown?"


def getCountryByAddress(addr):
	isLocal = ipaddress.ip_address(addr).is_private

	if isLocal:
		return "Local"
	else:
		handler = ipinfo.getHandler('cd401792e0fbc4')
		details = handler.getDetails(addr)
		return details.country_name


def updateConnections(addr):
	conn = openDB("/home/alex/socket/connections.db")

	count = queryConnectionCount(conn, addr)

	cur = conn.cursor()

	SQL = ""
	country = ""
	if count == 0:
		SQL = 'INSERT INTO addresses VALUES ((?), 1, (?))'
		country = getCountryByAddress(addr)
		cur.execute(SQL, (addr, country))
	else:
		SQL = 'UPDATE addresses SET count = count + 1 WHERE address = (?)'
		cur.execute(SQL, (addr,))
		country = queryConnectionCountry(conn, addr)

	conn.commit()
	conn.close()

	return (count + 1, country)
