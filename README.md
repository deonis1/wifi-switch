# wifi-switch
Esp-8266 enabled wifi switch

The code is based on micropython 1.9.4 and depends on ujson, ntptime, and other standard libraries.

Usage:

1) Set the board IP, port and your time difference from UTC. Is you use ESP32 and set your IP manually this IP should be the same as the one defined in your network config.

2) Upload .py and .html files to your esp MicroPython-enabled board and restart the board.

This code was tested on Nodemcu and esp-12

