#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read data from a QMC5883L magnetic sensor, covering a full turn
around the Z axis (i.e. on the X-Y plane). During the acquiring
phase, it shows a curses interface to give a feedback on how
many points were acquired and at what turning angle. When enough
data is acquired (or when the "Q" key is pressed), it saves a
text file with the raw "X Y Z" coordinates.
"""

import curses
import datetime
import math
import textwrap
import time
import signal
import sys
import py_qmc5883l

__author__ = "Niccolo Rigacci"
__copyright__ = "Copyright 2018 Niccolo Rigacci <niccolo@rigacci.org>"
__license__ = "GPLv3-or-later"
__email__ = "niccolo@rigacci.org"
__version__ = "0.1.1"

# Subdivide the entire circle in sectors, to group samples.
SECTORS_COUNT = 36
# How many samples to get per each sector.
SAMPLES_PER_SECTOR = 50

# Size of dial, in screen characters.
DIAL_WIDTH = 37
DIAL_HEIGHT = 19
BORDER_X = 4
BORDER_Y = 2

# Measured values range
SENSOR_MIN_VAL = -32768
SENSOR_MAX_VAL =  32767

RAW_DATA_FILE = "magnet-data_%s.txt" % (datetime.datetime.now().strftime('%Y%m%d_%H%M'),)

# ------------------------------------------------------------------------
# Calculate the size of screen objects.
# ------------------------------------------------------------------------
DIAL_RADIUS_X = float((DIAL_WIDTH - 1)/ 2.0)
DIAL_RADIUS_Y = float((DIAL_HEIGHT -1) / 2.0)
SECTOR_WIDTH = (2 * math.pi) / SECTORS_COUNT
TOTAL_WIDTH = DIAL_WIDTH + BORDER_X * 2
TOTAL_HEIGHT = DIAL_HEIGHT + BORDER_Y * 2

# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
def print_at(x, y, string, attr=curses.A_NORMAL):
    global stdscr
    try:
        stdscr.addstr(y, x, string, attr)
        stdscr.refresh()
    except:
        pass


# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
def terminate_handler(sig, frame):
    curses.endwin()
    sys.exit(1)

# ------------------------------------------------------------------------
# Initialize the magnetic sensor and screen curses.
# ------------------------------------------------------------------------
sensor = py_qmc5883l.QMC5883L()
signal.signal(signal.SIGINT, terminate_handler)
stdscr = curses.initscr()
# Hide the cursor and make getch() non-blocking.
curses.curs_set(0)
curses.noecho()
stdscr.nodelay(1)
stdscr.refresh()

# Draw a box.
print_at(0, 0, "-" * TOTAL_WIDTH)
print_at(0, TOTAL_HEIGHT - 1, "-" * TOTAL_WIDTH)
for i in range(1, TOTAL_HEIGHT-1):
    print_at(0, i, "|")
    print_at(TOTAL_WIDTH-1, i, "|")
msg = 'Do a complete rotation of the sensor on the XY plane. When enough samples are acquired, each sector will be marked with an "#".'
print_at(0, TOTAL_HEIGHT+2, textwrap.fill(msg, TOTAL_WIDTH))

# Inizialize samples dictionary and print dial on screen.
SAMPLES = {}
for i in range(0, SECTORS_COUNT):
    SAMPLES[i] = []
    angle = SECTOR_WIDTH * i
    DOT_X = BORDER_X + int(DIAL_RADIUS_X + DIAL_RADIUS_X * math.sin(angle))
    DOT_Y = BORDER_Y + int(DIAL_RADIUS_Y - DIAL_RADIUS_Y * math.cos(angle))
    print_at(DOT_X, DOT_Y, ".")
print_at(BORDER_X + int(DIAL_RADIUS_X), BORDER_Y + int(DIAL_RADIUS_Y), '+')
print_at(BORDER_X + int(DIAL_RADIUS_X), BORDER_Y - 1, 'N')
print_at(BORDER_X + int(DIAL_RADIUS_X), BORDER_Y + DIAL_HEIGHT, 'S')
print_at(BORDER_X + DIAL_WIDTH, BORDER_Y + int(DIAL_RADIUS_Y),  'E')
print_at(BORDER_X - 1, BORDER_Y + int(DIAL_RADIUS_Y), 'W')

# Loop to acquire data for the entire circumference.
completed_sectors = 0
NEEDLE_X = NEEDLE_Y = 1
while True:
    (x, y, z) = sensor.get_magnet_raw()
    if x is not None and y is not None:
        # Angle on the XY plane from magnetic sensor.
        angle = math.atan2(y, x)
        if angle < 0:
            angle += 2 * math.pi
        sector = int(angle / SECTOR_WIDTH)
        sampled = len(SAMPLES[sector])
        # Needle angle, rounded to sector center.
        needle_angle = ((2 * math.pi) / SECTORS_COUNT) * sector
        # Hide compass needle at previous position.
        print_at(NEEDLE_X, NEEDLE_Y, " ")
        # Print compass needle.
        NEEDLE_X = BORDER_X + int(DIAL_RADIUS_X + DIAL_RADIUS_X * 0.8 * math.sin(needle_angle))
        NEEDLE_Y = BORDER_Y + int(DIAL_RADIUS_Y - DIAL_RADIUS_Y * 0.8 * math.cos(needle_angle))
        print_at(NEEDLE_X, NEEDLE_Y, "O", curses.A_REVERSE)
        print_at(0, TOTAL_HEIGHT, "(X, Y) = (%s, %s), Compass: %s deg"
                % ("{:6d}".format(x), "{:6d}".format(y), "{:5.1f}".format(math.degrees(angle))))
        if sampled < SAMPLES_PER_SECTOR:
            DOT_X = BORDER_X + int(DIAL_RADIUS_X + DIAL_RADIUS_X * math.sin(needle_angle))
            DOT_Y = BORDER_Y + int(DIAL_RADIUS_Y - DIAL_RADIUS_Y * math.cos(needle_angle))
            SAMPLES[sector].append([x, y, z])
            sampled += 1
            completed = int(10 * (float(sampled) / SAMPLES_PER_SECTOR))
            if completed < 10:
                completed = str(completed)
                attr = curses.A_NORMAL
            else:
                completed = '#'
                attr = curses.A_REVERSE
            print_at(DOT_X, DOT_Y, completed, attr)
            if sampled >= SAMPLES_PER_SECTOR:
                completed_sectors += 1
            if completed_sectors >= SECTORS_COUNT:
                break
            time.sleep(0.10)
    time.sleep(0.05)
    key = stdscr.getch()
    if key == ord('q'):
        break
curses.endwin()

# Print raw values.
with open(RAW_DATA_FILE, "w") as f:
    for i in range(0, SECTORS_COUNT):
        if len(SAMPLES[i]) > 0:
            for s in SAMPLES[i]:
                line = "%.1f %.1f %.1f" % (s[0], s[1], s[2])
                f.write(line + "\n")
print(u'Raw data written to file "%s"' % (RAW_DATA_FILE,))
