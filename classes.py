import RPi.GPIO as GPIO
from datetime import datetime
from datetime import timedelta

class Relay(object):
	def __init__(self, pin, name, invertSignals = False):
		self.name = name
		self.enabled = False
		self.offTime = datetime.now() 						 # starts off
		self.onTime = datetime.now() - timedelta(seconds=60) # just needs to be before offTime
		self.pin = pin

		if invertSignals:
			self.SIG_ENABLED = 0
			self.SIG_DISABLED = 1
		else:
			self.SIG_ENABLED = 1
			self.SIG_DISABLED = 0

class Configuration(object):
	def __init__(self, revision):
		self.relays = []
		self.revision = revision

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

	def getNames(self):
		names = []
		for relay in self.relays:
			names.append(relay.name)

		return names

	def setRelayState(self, idPos, state):
		self.relays[idPos].enabled = state

		if state == True:
			self.relays[idPos].offTime = -1
		else:
			self.relays[idPos].offTime = datetime.now()

	def setRelayTimer(self, idPos, duration, delay=0):
		self.relays[idPos].onTime = datetime.now() + timedelta(seconds=delay)
		self.relays[idPos].offTime = datetime.now() + timedelta(seconds=duration) + timedelta(seconds=delay)


	def getRelayOffTime(self, idPos):
		return self.relays[idPos].offTime

	def getRelayOnTime(self, idPos):
		return self.relays[idPos].onTime

	def getRelay(self, idPos):
		return self.relays[idPos]