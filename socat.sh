#!/bin/bash

IP="127.0.0.1"
PORT=54321

if [ -n "$2" ]; then
	PORT=$2
	IP=$1
elif [ -n "$1" ]; then
	IP=$1
fi

echo "Starting SOCAT: $IP $PORT"

while true; do 
	socat pty,link=/dev/ttyACM0,raw,echo=0,waitslave "tcp:$IP:$PORT" > /dev/null 2> /dev/null
	sleep 0.5 # Be nice if the serial port or the socket closes
done
