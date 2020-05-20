#!/usr/bin/env python3

from database import openDB
import os
from termcolor import colored

barLength = int(os.popen('stty size', 'r').read().split()[1]) - 21
titles = ("Country Name", "Count")

bars = ['on_red','on_blue','on_yellow','on_green','on_magenta','on_cyan']

def main():
	conn = openDB("connections.db")
	cur = conn.cursor()

	total = cur.execute("select sum(count) from addresses").fetchone()[0]
	countryMax = 0

	SQL = 'select country, sum(count) from addresses group by country order by sum(count) desc'
	i = 0


	for row in cur.execute(SQL):
		country = row[0]
		count = row[1]

		if countryMax == 0:
			countryMax = count
			centerPad = barLength-len(str(countryMax)) - 1
			print(f"{titles[0]:>20}|0{titles[1]:^{centerPad}}{countryMax}")

		length = int((count/countryMax)*barLength)
		print(f"{country:>20}|"+colored(f"{count:>{length}}", "white", bars[i], attrs=['bold', 'dark']))
		i = (i+1)%3

	conn.close()

if __name__ == "__main__":
	main()