#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Operates the AHA entryway"""

from __future__ import print_function
import nfc
from nfc.clf import RemoteTarget
import sys
import time
import datetime
import ldap
import ldap.filter
import select
import termios
import threading
from mem_top import mem_top
import logging
import RPi.GPIO as GPIO
import resource

#Set up file logging
logging.basicConfig(filename="/var/log/door.log", level=logging.DEBUG, format="%(asctime)s : %(levelname)s - %(message)s")

# The string we use to open the NFC reader with nfcpy.
# We assume the device is connected with a USB->serial adapter,
# which means it should be located at /dev/ttyUSB0 or similar.
# Using 'tty:USB' seems to scan through all /dev/ttyUSB* devices until it finds a reader, which
# is probably helpful, in case it randomly jumps to another location (e.g. ttyUSB0->ttyUSB1),
# as USB serial devices sometimes do.
nfcReaderDev = 'tty:USB'

#GPIO assignments
innerDoorPin = 11
outerDoorPin = 13
exitButtonPin = 12

#Time allowed for door unlock state.
unlockDelay = 10

# Return value for this program.  Non-zero is an error.
ret = 0

class poller (threading.Thread):
	def __init__(self, threadID, clf):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.clf = clf

	def run(self):
		self.poll_reader()

	def poll_reader(self):
		# Add a detect event on the request-to-exit button.
		GPIO.add_event_detect(exitButtonPin, GPIO.RISING, bouncetime = unlockDelay*1000)
		while(True):
			# Open the door for {unlockDelay} seconds if we get a request to exit event from the button on the inside.
			if GPIO.event_detected(exitButtonPin):
				GPIO.output(innerDoorPin, GPIO.LOW)
				print("Someone wants to exit...")
				logging.debug("Exit requested!")
				time.sleep(unlockDelay)
				GPIO.output(innerDoorPin, GPIO.HIGH)
			# Scan for NFC targets
			try:
				target = self.clf.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'))
			except IOError as e:
				print("Caught exception:", e)
				logging.debug("Poller: caught exception: %s", e)

			if target is not None and target.sdd_res is not None:
				cardUID = ""
				# Convert the card ID from hexadecimal into a string, and limit it to the first 8 characters.
				cardUID = target.sdd_res.hex()[0:8]
				# Do LDAP lookup for 24-hour members with this card ID in their employeeNumber field.
				# Format LDAP query string
				accessFilter = ldap.filter.filter_format('(&(cn=*)(memberOf=cn=24hour,cn=groups,dc=hub,dc=allhandsactive,dc=com)(employeeNumber=%s))', [cardUID])
				# Attempt to connect to the LDAP server with the provided credentials 
				l = ldap.initialize("ldap://<THE_LDAP_SERVER_ADDRESS>")
				l.simple_bind_s("uid=root,cn=users,dc=hub,dc=allhandsactive,dc=com","<THE_LDAP_SERVER_PASSWORD>")
				# Run the LDAP query
				ldap_res = l.search_s('cn=users,dc=hub,dc=allhandsactive,dc=com', ldap.SCOPE_SUBTREE, accessFilter, ['uid'])
				if(len(ldap_res) > 0):
					logging.debug("LDAP results: %s", ldap_res)
					for dn, entry in ldap_res:
						logging.debug("Granted!: %s %s", cardUID, entry['uid'])
						print("Granted!: ", cardUID, entry['uid'])
						GPIO.output(innerDoorPin, GPIO.LOW)
						time.sleep(unlockDelay)
						GPIO.output(innerDoorPin, GPIO.HIGH)
						# Clear exit events.
						GPIO.remove_event_detect(exitButtonPin)
						GPIO.add_event_detect(exitButtonPin, GPIO.RISING, bouncetime = unlockDelay*1000)
				else:
					print("Denied!: ", cardUID)
					logging.debug("Denied!: %s", cardUID)
				l.unbind()
			# Poll card reader once per second
			time.sleep(1)

try:
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup([innerDoorPin,outerDoorPin], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(exitButtonPin, GPIO.IN)

	# Initialize the NFC reader.
	clf = nfc.ContactlessFrontend()
	clf.open(nfcReaderDev)

	if clf.device is None:
		raise Exception("No NFC devices found!")

	logging.debug("NFC reader: %s opened", clf.device)
	
	try:
		# Just keep reading the card information indefinitely.
		while(True):
			# Set up thread to run the card polling loop.
			myPoller = poller(str(0), clf)
			myPoller.daemon = True
			myPoller.start()
			print("Poller started -- Main thread monitoring poller thread...")
			logging.debug("Poller started -- Main thread monitoring poller thread.")
			
			while(True):
				# Check if the thread is still alive, and if not we should restart it.
				if myPoller.is_alive() is not True:
					break
				# Get the process memory usage in kilobytes.
				memusage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
				# Prevent the process from using more than 64M of memory.
				if(memusage > 65536):
					raise MemoryError("Exceeded allowed memory usage.")

				# Print a time-stamped heartbeat so I know this POS hasn't crashed yet.
				#tstamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				#print(tstamp, ": Still alive...")
				# Wait another 60 seconds until we check on the thread again.
				time.sleep(60)

	except MemoryError:
		raise
	except Exception as e:
		print("Caught exception: ", e)
		logging.debug("Poller loop caught exception: %s", e)
	finally:
		# Clear event detection on the exit button, so we don't have problems trying to add another.
		GPIO.remove_event_detect(exitButtonPin)
		print("Poller thread exited due to exception")
		logging.debug("Poller thread exited due to exception")
except MemoryError as e:
	print("Memory Error: ", e)
	logging.exception("%s: Memory error!", e)
	ret = 42
	raise
except (KeyboardInterrupt, SystemExit):
	print("Exiting gracefully!")
	logging.exception("Exiting gracefully!")
except Exception as e:
	print(e, ": Exiting ungracefully...")
	logging.exception("%s: Exiting ungracefully!", e)
	ret = 1
finally:
	logging.debug("Shutting down...")
	# Attempt to terminate the poller thread, 10 second timeout
	if myPoller is not None and myPoller.is_alive():
		myPoller.join(10)
		if myPoller.is_alive() is True:
			logging.debug("...Couldn't terminate poller thread -- exiting anyway")
		else:
			logging.debug("...Shut down poller thread")
	# Clean up GPIOs
	GPIO.cleanup([innerDoorPin,outerDoorPin,exitButtonPin])
	logging.debug("...Clean up GPIO")
	# Close card reader.
	# This is important, else might have to physically reconnect the reader's USB plug to successfully pick it up again with clf.open().
	if clf is not None:
		clf.close()
		logging.debug("...Closing NFC reader device")
	sys.exit(ret)
