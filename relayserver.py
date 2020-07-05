#!/usr/bin/env python3

# Written By Alexander Laevens
# May 2020
import socket
import threading
import sys
import LCD1602
import RPi.GPIO as GPIO
import time
import os
from w1thermsensor import W1ThermSensor
from classes import *
from datetime import datetime
from datetime import timedelta
from database import *
from pathlib import Path

DEF_PORT = 5050
DEF_HOST = socket.gethostbyname(socket.gethostname())
DEF_ADDR = (DEF_HOST, DEF_PORT)

tSensor = None

config = None

class Logging():
    logDirectory = "logs"
    logFile = "latest.log"

    def __init__(self, doPrintLogs, doFileLogs, printLevel = -1, fileLevel = -1):
        self.doPrintLogs = doPrintLogs
        self.doFileLogs = doFileLogs
        self.printLevel = printLevel
        self.fileLevel = fileLevel

        self.fileHandle = None
        self.lastLogDate = (datetime.now() - timedelta(days=1)).date() # needs to be in the past on init

        if self.doFileLogs:
            script = Path(sys.argv[0])
            cwd = script.parts[:-1]

            fullLogPath = os.path.join(*cwd, self.logDirectory)
            if not os.path.exists(fullLogPath):
                os.mkdir(fullLogPath)

            self.fileHandle = open(os.path.join(fullLogPath, self.logFile), "a")

    def __del__(self):
        if self.fileHandle != None:
            print("closing logger")
            self.fileHandle.close()


    def printLog(self, text, level = 0):
        if self.doPrintLogs and (level <= self.printLevel or self.printLevel == -1):
            print(text)

    def fileLog(self, text, level = 0):
        if self.doFileLogs and self.fileHandle != None and (level <= self.fileLevel or self.fileLevel == -1):
            self.fileHandle.write(text+"\n")
            self.fileHandle.flush()

    def log(self, text, level = 0):
        today = datetime.now().date()
        if today > self.lastLogDate:
            dateString = today.strftime("%b %d, %Y")
            toLog = f"{'='*20} [{dateString}] {'='*20}"
            self.printLog(toLog)
            self.fileLog(toLog)

            self.lastLogDate = today

        self.printLog(text, level)
        self.fileLog(text, level)

logging = Logging(True, True, -1, 1)

def configure():
    global config
    config = Configuration(1)
    config.addRelay(Relay(11, "Red", True))
    config.addRelay(Relay(12, "Green", True))
    config.addRelay(Relay(13, "Blue", True))
    config.addRelay(Relay(15, "Yellow", True))

def startRelayThreads():
    for i in range(len(config.getPins())):
        thread = threading.Thread(target=relayHandler,args=(i,))
        thread.daemon = True
        thread.start()

def recvString(conn):
    header = conn.recv(2)
    msgLen = int.from_bytes(header, byteorder='big')
    msg = conn.recv(msgLen).decode('utf-8')
    return msg

def SEND(conn, msg):
    toSend = msg.encode("utf-8")
    conn.send(len(toSend).to_bytes(2, byteorder='big'))
    conn.send(toSend)

def getTimeString():
    t = datetime.now()
    current_time = t.strftime("%I:%M %p")
    return str(current_time)

def relayHandler(idPos):
    relay = config.getRelay(idPos)
    pin = relay.pin
    SIG_ON = relay.SIG_ENABLED
    SIG_OFF = relay.SIG_DISABLED
    GPIO.setmode(GPIO.BOARD)

    print("ON:", SIG_ON, "OFF:", SIG_OFF)

    while True:
        try:
            timeOff = config.getRelayOffTime(idPos)
            timeOn = config.getRelayOnTime(idPos)
            timeCurrent = datetime.now()

            if timeOff == -1:               # manual On
                #GPIO.output(pin, GPIO.LOW)
                GPIO.output(pin, SIG_ON)
            elif timeCurrent >= timeOff:
                #GPIO.output(pin, GPIO.HIGH)
                GPIO.output(pin, SIG_OFF)
            elif timeCurrent < timeOff and timeCurrent >= timeOn:
                #GPIO.output(pin, GPIO.LOW)
                GPIO.output(pin, SIG_ON)
            else:
                #GPIO.output(pin, GPIO.HIGH)
                GPIO.output(pin, SIG_OFF)

            time.sleep(0.2)

        except:
            print("Stopping relay thread")
            break

def clientHandler(conn, addr):
    threadName = threading.currentThread().getName()
    logging.log(f"[{threadName} : {getTimeString()}] Connection from: {addr}", 1)
    
    while True:
        command = recvString(conn)
        logging.log(f"[{threadName} : {getTimeString()}] COMMAND: '{command}'", 1)

        if command == "DISCONNECT":
            logging.log(f"[{threadName} : {getTimeString()}] Close...", 2)
            conn.close()
            break

        elif command == "SETRELAY":
            relayNum = int(recvString(conn))
            setTo = int(recvString(conn))
            relay = config.getRelay(relayNum)
            logging.log(f"[{threadName} : {getTimeString()}] \tRelay #{relayNum} [{relay.name}] Set to: {setTo}", 2)

            config.setRelayState(relayNum, setTo)

        elif command == "TIMERELAY":
            relayNum = int(recvString(conn))
            duration = int(recvString(conn))
            delay = int(recvString(conn))
            logging.log(f"[{threadName} : {getTimeString()}] \tRelay #{relayNum} On for: {duration} seconds after {delay} seconds", 2)

            config.setRelayTimer(relayNum, duration, delay)

        elif command == "GETTEMP":
            temp = tSensor.get_temperature()
            logging.log(f"[{threadName} : {getTimeString()}] \tCurrent Temperature: {temp}°C", 2)
            SEND(conn, str(temp))

        elif command == "GETREVISION":
            SEND(conn, str(config.revision))

        elif command == "GETCONFIG":
            relayLabels = config.getNames()
            SEND(conn, str(len(relayLabels)))

            for label in relayLabels:
                SEND(conn, label)


        elif command == "":
            conn.close()

def initGPIO(pins):
    global tSensor
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pins, GPIO.OUT)
    GPIO.output(pins, GPIO.HIGH)
    tSensor = W1ThermSensor()  

def cleanGPIO(pins):
    GPIO.output(pins, GPIO.HIGH)
    GPIO.cleanup()

def start(ADDR):
    HOST, PORT = ADDR
    logging.log(f"[MAIN : {getTimeString()}] Hosting on: {HOST}:{PORT}")

    configure()
    initGPIO(config.getPins())
    startRelayThreads()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(ADDR)

    logging.log(f"[MAIN : {getTimeString()}] Listening....")
    s.listen()
    while True:
        try:
            conn, addr = s.accept()
            count, country = updateConnections(addr[0])
            logging.log(f"[MAIN : {getTimeString()}] New Connection: {addr[0]}, from {country}, has connected {count} time(s)")

            if country in ["Local", "Canada"]:
                logging.log(f"[MAIN : {getTimeString()}] Accepting Connection")
                thread = threading.Thread(target=clientHandler, args=(conn, addr))
                thread.start()
            else:
                logging.log(f"[MAIN : {getTimeString()}] Refusing connection")
                conn.close()
        except KeyboardInterrupt:
            logging.log(f"[MAIN : {getTimeString()}] Interrupted...Closing")
            s.close()
            cleanGPIO(config.getPins())
            break
        

if __name__ == "__main__":
    if len(sys.argv) == 2:
        HOST, PORT = sys.argv[1].split(":")
        HOST = socket.gethostbyname(HOST)
        PORT = int(PORT)
        logging.log(f"Using custom Host:Port: {HOST}:{PORT}")
        start((HOST, PORT))
    else:
        start(DEF_ADDR)

    del logging
