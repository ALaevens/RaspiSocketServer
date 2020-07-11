#!/bin/bash

declare -a pythonDependencies=(termcolor W1ThermSensor requests ipinfo RPi.GPIO)
declare -a aptDependencies=(python3-pip sqlite3 screen)

echo
echo
echo "Install apt dependencies"
for aptDep in "${aptDependencies[@]}"; do
   apt-get -y install $aptDep
done

echo
echo
echo "Install python dependencies"
for pyDep in "${pythonDependencies[@]}"; do
   python3 -m pip install $pyDep
done

echo
echo
echo "Setup DB"
sqlite3 connections.db < createdb.sql
