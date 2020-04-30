import socket
import threading
import sys
import LCD1602
import RPi.GPIO as GPIO

DEF_PORT = 5050
DEF_HOST = socket.gethostbyname(socket.gethostname())
DEF_ADDR = (DEF_HOST, DEF_PORT)

allPins = (11,12,13)
relayPin = 13
ledPins = (11, 12)
ledState = [False, False]

backlight = True

def RECV(conn):
    msgLen = int.from_bytes(conn.recv(2), byteorder='big')
    msg = conn.recv(msgLen)
    return msg

def toggleLed():
    for i in range(len(ledState)):
        ledState[i] = not ledState[i]
        if ledState[i]:
            GPIO.output(ledPins[i], GPIO.HIGH)
        else:
            GPIO.output(ledPins[i], GPIO.LOW)

def setLED(state):
    state = state.lower()
    if state == "green":
        ledState = [True, False]
        GPIO.output(11, GPIO.HIGH)
        GPIO.output(12, GPIO.LOW)
    elif state == "red":
        ledState = [False, True]
        GPIO.output(11, GPIO.LOW)
        GPIO.output(12, GPIO.HIGH)


def client_handler(conn, addr):
    threadName = threading.currentThread().getName()
    print(f"[{threadName}] Connection from: {addr}")
    while True:
        command = RECV(conn).decode("utf-8")
        print(f"[{threadName}] COMMAND: '{command}'")

        if command == "DISCONNECT":
            print(f"[{threadName}] Close...")
            conn.close()
            break

        elif command == "SETLCD":
            text = RECV(conn).decode("utf-8")
            print(f"[{threadName}] \tText: '{text}'")
            LCD1602.init(0x27, backlight)
            LCD1602.write(0, 0, text[:16])
            LCD1602.write(0, 1, text[16:32])

        elif command == "CLEARLCD":
            LCD1602.init(0x27, int(backlight))

        elif command == "SETLED":
            color = RECV(conn).decode("utf-8")
            print(f"[{threadName}] \tColor: '{color}'")
            setLED(color)

        elif command == "SETRELAY":
            setTo = int(RECV(conn).decode("utf-8"))
            print(f"[{threadName}] \tSet to: {setTo}")

            if setTo:
                GPIO.output(relayPin, GPIO.HIGH)
            else:
                GPIO.output(relayPin, GPIO.LOW)


    

def start(ADDR):
    HOST, PORT = ADDR
    print(f"[MAIN] Hosting on: {HOST}:{PORT}")

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(allPins, GPIO.OUT)
    GPIO.output(allPins, GPIO.LOW)
    GPIO.output(ledPins[0], GPIO.HIGH)
    ledState[0] = True

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(ADDR)

    print("[MAIN] Listening....")
    s.listen()
    while True:
        try:
            conn, addr = s.accept()
            print("[MAIN] Accepted Connection...")
            thread = threading.Thread(target=client_handler, args=(conn, addr))
            thread.start()
        except KeyboardInterrupt:
            print("[MAIN] Interrupted...Closing")
            s.close()
            GPIO.output(allPins, GPIO.LOW)
            GPIO.cleanup()
            break
        

if __name__ == "__main__":
    if len(sys.argv) == 2:
        HOST, PORT = sys.argv[1].split(":")
        HOST = socket.gethostbyname(HOST)
        PORT = int(PORT)
        print(f"Using custom Host:Port: {HOST}:{PORT}")
        start((HOST, PORT))
    else:
        start(DEF_ADDR)
