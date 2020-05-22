Socket server for use with an in development android app to do some home automation tasks.

Personal Use only

Running:
	Make cure relayserver.py and connectioninfo.py have execute permission

	Server:
		./relayserver.py CUSTOMHOST:PORT
		if a custom host and port is not specified, uses the ip of the local machine (in /etc/hosts/) and port 5050

	Connection Info:
		./connectioninfo.py
		Close the program with CTRL+C
