#!/usr/bin/env python3

# Written By Alexander Laevens
# May 2020
import socket
import threading
import sys
import LCD1602
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

DEF_PORT = 5050
DEF_HOST = socket.gethostbyname(socket.gethostname())
DEF_ADDR = (DEF_HOST, DEF_PORT)
DOLOGGING = True

allPins = (11, 12, 13, 15)

backlight = True
tSensor = None

def log(text):
    if DOLOGGING:
        print(text)

def RECV(conn):
    header = conn.recv(2)
    msgLen = int.from_bytes(header, byteorder='big')
    msg = conn.recv(msgLen)
    return msg

def SEND(conn, msg):
    toSend = msg.encode("utf-8")
    conn.send(len(toSend).to_bytes(2, byteorder='big'))
    conn.send(toSend)

def client_handler(conn, addr):
    global tSensor
    threadName = threading.currentThread().getName()
    log(f"[{threadName}] Connection from: {addr}")
    while True:
        command = RECV(conn).decode("utf-8")
        log(f"[{threadName}] COMMAND: '{command}'")

        if command == "DISCONNECT":
            log(f"[{threadName}] Close...")
            conn.close()
            break;

        elif command == "SETRELAY":
            relayNum = int(RECV(conn).decode("utf-8"))
            setTo = int(RECV(conn).decode("utf-8"))
            log(f"[{threadName}] \tRelay #{relayNum}")
            log(f"[{threadName}] \tSet to: {setTo}")

            if setTo:
                GPIO.output(allPins[relayNum], GPIO.LOW)
            else:
                GPIO.output(allPins[relayNum], GPIO.HIGH)

        elif command == "GETTEMP":
            temp = tSensor.get_temperature()
            log(f"[{threadName}] \tCurrent Temperature: {temp}°C")
            SEND(conn, str(temp))

        elif command == "":
            conn.close()

def initGPIO():
    global tSensor
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(allPins, GPIO.OUT)
    GPIO.output(allPins, GPIO.HIGH)
    tSensor = W1ThermSensor()  

def cleanGPIO():
    GPIO.output(allPins, GPIO.HIGH)
    GPIO.cleanup()

def start(ADDR):
    HOST, PORT = ADDR
    log(f"[MAIN] Hosting on: {HOST}:{PORT}")

    initGPIO()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(ADDR)

    log("[MAIN] Listening....")
    s.listen()
    while True:
        try:
            conn, addr = s.accept()
            log("[MAIN] Accepted Connection...")
            thread = threading.Thread(target=client_handler, args=(conn, addr))
            thread.start()
        except KeyboardInterrupt:
            log("[MAIN] Interrupted...Closing")
            s.close()
            cleanGPIO()
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
