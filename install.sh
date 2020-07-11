#1/bin/bash

declare -a pythonDependencies=(termcolor W1ThermSensor requests ipinfo RPi.GPIO)
declare -a aptDependencies=(python3-pip sqlite3 screen)


echo "Install apt dependencies"
for aptDep in "${aptDependencies[@]}"; do
   python3 -m pip install $aptDep
done

echo "Install python dependencies"
for pyDep in "${pythonDependencies[@]}"; do
   python3 -m pip install $pyDep
done

sqlite3 connections.db < createdb.sql
