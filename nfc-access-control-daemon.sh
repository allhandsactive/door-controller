#!/bin/bash
until python /home/gatekeeper/nfc-access-control.py; do
	echo "Server 'nfc-access-control.py' crashed with exit code $?.  Respawning.." >&2
	sleep 1
done
