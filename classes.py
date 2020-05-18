import RPi.GPIO as GPIO
from datetime import datetime
from datetime import timedelta

class Relay(object):
	def __init__(self, pin, name):
		self.name = name
		self.enabled = False
		self.offTime = datetime.now()
		self.pin = pin

class Configuration(object):
	def __init__(self):
		self.relays = []

	def addRelay(self, relay):
		for i in range(len(self.relays)):
			temp = self.relays[i]
			if temp.pin == relay.pin:
				self.relays[i] = relay
				return

		self.relays.append(relay)

	def getPins(self):
		pins = []
		for relay in self.relays:
			pins.append(relay.pin)

		return tuple(pins)

	def setRelayState(self, idPos, state):
		self.relays[idPos].enabled = state

		if state == True:
			self.relays[idPos].offTime = -1
		else:
			self.relays[idPos].offTime = datetime.now()

	def setRelayTimer(self, idPos, duration):
		self.relays[idPos].offTime = datetime.now() + timedelta(seconds=duration)


	def getRelayOffTime(self, idPos):
		return self.relays[idPos].offTime

	def getRelay(self, idPos):
		return self.relays[idPos]