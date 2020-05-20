#!/usr/bin/env python3

# Written By Alexander Laevens
# May 2020
import socket
import threading
import sys
import LCD1602
import RPi.GPIO as GPIO
import time
from w1thermsensor import W1ThermSensor
from classes import *
from datetime import datetime
from datetime import timedelta
from database import *

DEF_PORT = 5050
DEF_HOST = socket.gethostbyname(socket.gethostname())
DEF_ADDR = (DEF_HOST, DEF_PORT)
DOLOGGING = True

tSensor = None

config = None

def configure():
    global config
    config = Configuration()
    config.addRelay(Relay(11, "Red"))
    config.addRelay(Relay(12, "Green"))
    config.addRelay(Relay(13, "Blue"))
    config.addRelay(Relay(15, "Yellow"))

def startRelayThreads():
    for i in range(len(config.getPins())):
        thread = threading.Thread(target=relayHandler,args=(i,))
        thread.daemon = True
        thread.start()

def log(text):
    if DOLOGGING:
        print(text)

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
    pin = config.getRelay(idPos).pin

    while True:
        timeOff = config.getRelayOffTime(idPos)
        timeCurrent = datetime.now()
        if timeOff == -1:
            GPIO.output(pin, GPIO.LOW)
        elif timeCurrent > timeOff:
            GPIO.output(pin, GPIO.HIGH)
        elif timeCurrent < timeOff:
            GPIO.output(pin, GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.HIGH)

        time.sleep(0.2)

def clientHandler(conn, addr):
    threadName = threading.currentThread().getName()
    log(f"[{threadName} : {getTimeString()}] Connection from: {addr}")
    
    while True:
        command = recvString(conn)
        log(f"[{threadName} : {getTimeString()}] COMMAND: '{command}'")

        if command == "DISCONNECT":
            log(f"[{threadName} : {getTimeString()}] Close...")
            conn.close()
            break

        elif command == "SETRELAY":
            relayNum = int(recvString(conn))
            setTo = int(recvString(conn))
            log(f"[{threadName} : {getTimeString()}] \tRelay #{relayNum} Set to: {setTo}")

            config.setRelayState(relayNum, setTo)

        elif command == "TIMERELAY":
            relayNum = int(recvString(conn))
            seconds = int(recvString(conn))
            log(f"[{threadName} : {getTimeString()}] \tRelay #{relayNum} On for: {seconds} seconds")

            config.setRelayTimer(relayNum, seconds)

        elif command == "GETTEMP":
            temp = tSensor.get_temperature()
            log(f"[{threadName} : {getTimeString()}] \tCurrent Temperature: {temp}°C")
            SEND(conn, str(temp))

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
    log(f"[MAIN] Hosting on: {HOST}:{PORT}")

    configure()
    initGPIO(config.getPins())
    startRelayThreads()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(ADDR)

    log("[MAIN] Listening....")
    s.listen()
    while True:
        try:
            conn, addr = s.accept()
            count, country = updateConnections(addr[0])
            log(f"[MAIN] New Connection: {addr[0]}, from {country}, has connected {count} time(s)")

            if country in ["Local", "Canada"]:
                log("[Main] Accepting Connection")
                thread = threading.Thread(target=clientHandler, args=(conn, addr))
                thread.start()
            else:
                log("[MAIN] Refusing connection")
                conn.close()
        except KeyboardInterrupt:
            log("[MAIN] Interrupted...Closing")
            s.close()
            cleanGPIO(config.getPins())
            break
        

if __name__ == "__main__":
    if len(sys.argv) == 2:
        HOST, PORT = sys.argv[1].split(":")
        HOST = socket.gethostbyname(HOST)
        PORT = int(PORT)
        log(f"Using custom Host:Port: {HOST}:{PORT}")
        start((HOST, PORT))
    else:
        start(DEF_ADDR)
