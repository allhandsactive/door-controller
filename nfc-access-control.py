#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Operates the AHA entryway"""

from __future__ import print_function
import nfc
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
logging.basicConfig(filename="door.log", level=logging.DEBUG, format="%(asctime)s : %(levelname)s - %(message)s")

verbose = False
mask = 0xff
max_device_count = 1
max_target_count = 1

#GPIO assignments
innerDoorPin = 11
outerDoorPin = 13
exitButtonPin = 12

#Time allowed for door unlock state.
unlockDelay = 10

hardCodedCards = [
	'12345678', #someone's hardcoded card, if needed?
]

# Return value for this program.  Non-zero is an error.
ret = 0

class poller (threading.Thread):
	def __init__(self, threadID, nfc, pnd, nm): #nfc, pnd):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.nfc = nfc
		self.pnd = pnd
		self.nm = nm
		#self.res = None
		#self.ant = None

	def run(self):
		#print("Starting poll for ", self.threadID, ": ", self.nfc.device_get_connstring(self.pnd))
		self.poll_reader()

	def poll_reader(self):
		# Add a detect event on the request-to-exit button.
		GPIO.add_event_detect(exitButtonPin, GPIO.RISING, bouncetime = unlockDelay*1000)
		while(True):
			# Open the door for {unlockDelay} seconds if we get a request to exit event from the button on the inside.
			if GPIO.event_detected(exitButtonPin):
			#if GPIO.input(exitButtonPin):
				GPIO.output(innerDoorPin, GPIO.LOW)
				print("Someone wants to exit...")
				logging.debug("Exit requested!")
				time.sleep(unlockDelay)
				GPIO.output(innerDoorPin, GPIO.HIGH)
			# List ISO14443A targets
			try:
				nt = self.nfc.target()
				# This method blocks constantly, and crashes the Pi randomly.
				#ret = self.nfc.initiator_select_passive_target(self.pnd, self.nm, 0, 0, nt)
				# This less-awful method seems to eat memory like popcorn, and if not handled gracefully, will ultimately crash the Pi.
				res, ant = self.nfc.initiator_list_passive_targets(self.pnd, self.nm, max_target_count)
				#print("sel_pass_targ: ", ret)
			except:
				raise
			#if (ret > 0):
			if (verbose or (res > 0)):
				#print(res, self.threadID, ": ISO14443A passive target(s) found")
			#for n in range(res):
				cardUID = ""
				#userPass = ""
					
				#self.nfc.print_nfc_target(ant[n], verbose)
				cardUID = ant[0].nti.nai.abtUid.hex()[0:8]
				#cardUID = nt.nti.nai.abtUid.hex()[0:8]
				#print(self.threadID, ": Got card UID:", cardUID)
				#logging.debug("Got card UID %s", cardUID)
				#accessFilter = ldap.filter.filter_format('(&(cn=*)(description=%s)(postalAddress=%s))', [cardUID, userPass])
				
				accessFilter = ldap.filter.filter_format('(&(cn=*)(memberOf=cn=24hour,cn=groups,dc=hub,dc=allhandsactive,dc=com)(employeeNumber=%s))', [cardUID])
				l = ldap.initialize("ldap://<THELDAPSERVERIP>")
				l.simple_bind_s("uid=root,cn=users,dc=hub,dc=allhandsactive,dc=com","<THELDAPPASSWORD>")
				ldap_res = l.search_s('cn=users,dc=hub,dc=allhandsactive,dc=com', ldap.SCOPE_SUBTREE, accessFilter, ['uid'])
				if(len(ldap_res) > 0):
					logging.debug("LDAP results: %s", ldap_res)
					for dn, entry in ldap_res:
						#if(cardUID in hardCodedCards):
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
				
				#logging.debug(mem_top(limit=20,width=2000))
				
				l.unbind()
					#Get user input for password -- 20 second timeout.
					#This password stuff has been scrubbed since nobody was super gung-ho about adding a second authentication factor.  It's here for posterity, I guess.
					#TODO: Figure out a thread-safe way to do this! Currently if more than one thread is waiting for input, indeterminate results may occur.
					#if(self.threadID != "1"):
						# Clear out input buffer before taking raw input.
						#termios.tcflush(sys.stdin,termios.TCIFLUSH)
						#print(self.threadID, ": Waiting for password!")
						#i, o, e = select.select([sys.stdin], [], [], 20)
						#if(i):
						#	userPass = sys.stdin.readline().strip()
							#print(self.threadID, ": Password is:", userPass)
						#else:
							#print(self.threadID, ": Password timeout")
							
						#accessFilter = ldap.filter.filter_format('(&(cn=*)(description=%s)(<PASSWORDFIELD>=%s))', [cardUID, userPass])
					#else:
					#	accessFilter = ldap.filter.filter_format('(&(cn=*)(description=%s))', [cardUID])
					#TODO: LDAP requests includes some kind of group selector? (e.g. memberOf).
					#TODO: Setup up SSL LDAP to secure password data.
					#l = ldap.initialize("ldap://<THELDAPSERVERIP>")
					#l.simple_bind_s("","")
					#ldap_res = l.search_s('ou=users,dc=<SOMEDC>', ldap.SCOPE_SUBTREE, accessFilter)
					#print("Results: ", ldap_res)
					#if(len(ldap_res) > 0):
					#	print("Hooray!")
					#else:
					#	print("Boo!")
					#l.unbind()
			time.sleep(1)

try:
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup([innerDoorPin,outerDoorPin], GPIO.OUT, initial=GPIO.HIGH)
	GPIO.setup(exitButtonPin, GPIO.IN)

	context = nfc.init()

	# Display libnfc version
	#print("%s uses libnfc %s" %( sys.argv[0], nfc.__version__))

	connstrings = nfc.list_devices(context, max_device_count)
	szDeviceFound = len(connstrings)

	pnd = None
	
	if len(connstrings) == 0:
		raise Exception("No NFC devices found!")

	for i in range(szDeviceFound):
		pnd = nfc.open(context, connstrings[i]);
		if pnd is None:
			continue

	if(nfc.initiator_init(pnd)<0):
		nfc.perror(pnd, "nfc_initiator_init")
		raise Exception("Unable to initialize NFC reader!")

	print("NFC reader:", nfc.device_get_name(pnd), "(", nfc.device_get_connstring(pnd), ") opened")

	
	nm = nfc.modulation()
	nm.nmt = nfc.NMT_ISO14443A
	nm.nbr = nfc.NBR_106
	
	try:
		# Just keep reading the card information indefinitely.
		while(True):
			myPoller = poller(str(0), nfc, pnd, nm)
			myPoller.daemon = True
			myPoller.start()
			print("Poller started -- Main thread monitoring poller thread...")
			
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
				tstamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				print(tstamp, ": Still alive...")
				time.sleep(60)
			
			# Do nothing until myPoller fails somehow.
			#myPoller.join()
	except MemoryError:
		raise
	except Exception as e:
		print("Caught exception: ", e)
	finally:
		# Clear event detection on the exit button, so we don't have problems trying to add another.
		GPIO.remove_event_detect(exitButtonPin)
		print("Poller thread exited -- Attempting to restart...")
except MemoryError as e:
	print("Memory Error: ", e)
	logging.exception("Memory error!")
	ret = 42
	raise
except (KeyboardInterrupt, SystemExit):
	print("Exiting gracefully!")
	logging.exception("Exited gracefully!")
except Exception as e:
	print(e, ": Exiting ungracefully...")
	logging.exception("Exited ungracefully!")
	ret = 1
finally:
	# Stop all pollers.
	GPIO.cleanup([innerDoorPin,outerDoorPin,exitButtonPin])
	# This often causes a segfault which screws stuff up for a clean exit.  Not sure how necessary it is since we've exited anyhow.
	#if pnd is not None:
	#	nfc.close(pnd)
	nfc.exit(context)
	sys.exit(ret)
