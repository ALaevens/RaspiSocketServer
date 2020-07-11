Socket server for use with an in development android app to do some home automation tasks.

This server only intended to be run off of a RaspberryPi

Installing:
    - Do automated initial install with 'chmod +x install.sh && sudo ./install.sh'

    - To launch server from startup:
        runuser -l [USER] -c 'screen -dmS relayServer python3 [FULL RELAYSERVER.PY PATH]'

    - For convenience give relayserver.py and connectioninfo.py execute permission
        chmod +x relayserver.py
        chmod +x connectioninfo.py

    - If the server has difficulty binding to the proper ip address, define the static or DHCP reserved ip in /etc/hosts
        or run it with a defined host:port combination




Running:
	Make sure relayserver.py and connectioninfo.py have execute permission

	Server:
		./relayserver.py CUSTOMHOST:PORT
		if a custom host and port is not specified, uses the ip of the local machine (in /etc/hosts/) and port 5050

	Connection Info:
		./connectioninfo.py
		Close the program with CTRL+C
