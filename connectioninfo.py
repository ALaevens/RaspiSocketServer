#!/usr/bin/env python3

from database import openDB
import sys
import os
from termcolor import colored

bars = ['on_red','on_blue','on_magenta','on_yellow', 'on_green']

def makeGraph(conn):
	cur = conn.cursor()

	titles = ("Country Name", "Connection Count")
	nameLength = cur.execute("select max(len) from (select length(country) as len from addresses)").fetchone()[0]
	nameLength = max(nameLength, len(titles[0]))
	barLength = int(os.popen('stty size', 'r').read().split()[1]) - nameLength - 2

	total = cur.execute("select sum(count) from addresses").fetchone()[0]
	countryMax = 0

	SQL = 'select country, sum(count) from addresses group by country order by sum(count) desc'
	i = 0


	for row in cur.execute(SQL):
		country = row[0]
		count = row[1]

		if countryMax == 0:
			countryMax = count
			centerPad = barLength-len(str(countryMax))-1
			print(colored(f"{titles[0]:<{nameLength}}|0{titles[1]:^{centerPad}}{countryMax}", attrs=['underline']))

		length = int((count/countryMax)*barLength)
		if (len(str(count)) <= length):
			print(f"{country:>{nameLength}}|"+colored(f"{count:>{length}}", "white", bars[i], attrs=['bold', 'underline'])+"⎢")
		else:
			print(f"{country:>{nameLength}}|"+colored(f"{' '*length}", "white", bars[i], attrs=['bold', 'underline'])+f"⎢{count}")

		i = (i+1)%len(bars)

def makeTable(conn, country):
	cur = conn.cursor()

	SQL = 'select address, count from addresses where country = (?) collate nocase order by count desc'
	titles = ("Address", "Connections")

	cur.execute(SQL, (country,))
	data = cur.fetchall()
	
	if len(data) == 0:
		print(f"No data for selected country: '{country}'")
		return

	widths = (max(len(titles[0]),15), max(len(titles[1]),15))
	print(f"\n\nData from country: {country}")
	print(colored(f"{titles[0]:<{widths[0]}}|{titles[1]:<{widths[1]}}",attrs=['underline']))
	for row in data:
		address = row[0]
		count = row[1]
		print(colored(f"{address:>{widths[0]}}|{count:>{widths[1]}}",attrs=["underline"]))

	print(f"{len(data)} unique address(es)")
def main():
	script = sys.argv[0]
	path = script.split("/")
	conn = openDB("/".join(path[:-1]+["connections.db"]))
	makeGraph(conn)

	
	while True:
		try:
			country = input("\n\nFor more details, enter a country. To quit, Enter 'q' or press CTRL+C\n-> ")
			if country.lower() == 'q':
				break
			makeTable(conn, country)

		except (KeyboardInterrupt, EOFError) as e:
			break

	print("\n Cleaning up and closing.")
	conn.close()

if __name__ == "__main__":
	main()
