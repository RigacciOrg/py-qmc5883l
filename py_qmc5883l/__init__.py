# -*- coding: utf-8 -*-
"""
Python driver for the QMC5883L 3-Axis Magnetic Sensor.

Usage example:

  import py_qmc5883l
  sensor = py_qmc5883l.QMC5883L()
  m = sensor.get_magnet()
  print(m)

you will get three 16 bit signed integers, representing the values
of the magnetic sensor on axis X, Y and Z, e.g. [-1257, 940, -4970].
"""

import logging
import math
import time
import smbus

__author__ = "Niccolo Rigacci"
__copyright__ = "Copyright 2018 Niccolo Rigacci <niccolo@rigacci.org>"
__license__ = "GPLv3-or-later"
__email__ = "niccolo@rigacci.org"
__version__ = "0.1.1"

DFLT_BUS = 1
DFLT_ADDRESS = 0x0d

REG_XOUT_LSB = 0x00     # Output Data Registers for magnetic sensor.
REG_XOUT_MSB = 0x01
REG_YOUT_LSB = 0x02
REG_YOUT_MSB = 0x03
REG_ZOUT_LSB = 0x04
REG_ZOUT_MSB = 0x05
REG_STATUS_1 = 0x06     # Status Register.
REG_TOUT_LSB = 0x07     # Output Data Registers for temperature.
REG_TOUT_MSB = 0x08
REG_CONTROL_1 = 0x09    # Control Register #1.
REG_CONTROL_2 = 0x0a    # Control Register #2.
REG_RST_PERIOD = 0x0b   # SET/RESET Period Register.
REG_CHIP_ID = 0x0d      # Chip ID register.

# Flags for Status Register #1.
STAT_DRDY = 0b00000001  # Data Ready.
STAT_OVL = 0b00000010   # Overflow flag.
STAT_DOR = 0b00000100   # Data skipped for reading.

# Flags for Status Register #2.
INT_ENB = 0b00000001    # Interrupt Pin Enabling.
POL_PNT = 0b01000000    # Pointer Roll-over.
SOFT_RST = 0b10000000   # Soft Reset.

# Flags for Control Register 1.
MODE_STBY = 0b00000000  # Standby mode.
MODE_CONT = 0b00000001  # Continuous read mode.
ODR_10HZ = 0b00000000   # Output Data Rate Hz.
ODR_50HZ = 0b00000100
ODR_100HZ = 0b00001000
ODR_200HZ = 0b00001100
RNG_2G = 0b00000000     # Range 2 Gauss: for magnetic-clean environments.
RNG_8G = 0b00010000     # Range 8 Gauss: for strong magnetic fields.
OSR_512 = 0b00000000    # Over Sample Rate 512: less noise, more power.
OSR_256 = 0b01000000
OSR_128 = 0b10000000
OSR_64 = 0b11000000     # Over Sample Rate 64: more noise, less power.


class QMC5883L(object):
    """Interface for the QMC5883l 3-Axis Magnetic Sensor."""
    def __init__(self,
                 i2c_bus=DFLT_BUS,
                 address=DFLT_ADDRESS,
                 output_data_rate=ODR_10HZ,
                 output_range=RNG_2G,
                 oversampling_rate=OSR_512):

        self.address = address
        self.bus = smbus.SMBus(i2c_bus)
        self.output_range = output_range
        chip_id = self._read_byte(REG_CHIP_ID)
        if chip_id != 0xff:
            msg = "Chip ID returned 0x%x instead of 0xff; is the wrong chip?"
            logging.warning(msg, chip_id)
        self.mode_cont = (MODE_CONT | output_data_rate | output_range
                          | oversampling_rate)
        self.mode_stby = (MODE_STBY | ODR_10HZ | RNG_2G | OSR_64)
        self.mode_continuous()

    def __del__(self):
        """Once finished using the sensor, switch to standby mode."""
        self.mode_standby()

    def mode_continuous(self):
        """Set the device in continuous read mode."""
        self._write_byte(REG_CONTROL_2, SOFT_RST)  # Soft reset.
        self._write_byte(REG_CONTROL_2, INT_ENB)  # Disable interrupt.
        self._write_byte(REG_RST_PERIOD, 0x01)  # Define SET/RESET period.
        self._write_byte(REG_CONTROL_1, self.mode_cont)  # Set operation mode.

    def mode_standby(self):
        """Set the device in standby mode."""
        self._write_byte(REG_CONTROL_2, SOFT_RST)
        self._write_byte(REG_CONTROL_2, INT_ENB)
        self._write_byte(REG_RST_PERIOD, 0x01)
        self._write_byte(REG_CONTROL_1, self.mode_stby)  # Set operation mode.

    def _write_byte(self, registry, value):
        self.bus.write_byte_data(self.address, registry, value)
        time.sleep(0.01)

    def _read_byte(self, registry):
        return self.bus.read_byte_data(self.address, registry)

    def _read_word(self, registry):
        """Read a two bytes value stored as LSB and MSB."""
        low = self.bus.read_byte_data(self.address, registry)
        high = self.bus.read_byte_data(self.address, registry + 1)
        val = (high << 8) + low
        return val

    def _read_word_2c(self, registry):
        """Calculate the 2's complement of a two bytes value."""
        val = self._read_word(registry)
        if val >= 0x8000:  # 32768
            return val - 0x10000  # 65536
        else:
            return val

    def get_data(self):
        """Read data from magnetic and temperature data registers."""
        i = 0
        [x, y, z, t] = [None, None, None, None]
        while i < 20:  # Timeout after about 0.20 seconds.
            status = self._read_byte(REG_STATUS_1)
            if status & STAT_OVL:
                # Some values have reached an overflow.
                msg = ("Magnetic sensor overflow.")
                if self.output_range == RNG_2G:
                    msg += " Consider switching to RNG_8G output range."
                logging.warning(msg)
            if status & STAT_DOR:
                # Previous measure was read partially, sensor is in Data Lock.
                x = self._read_word_2c(REG_XOUT_LSB)
                y = self._read_word_2c(REG_YOUT_LSB)
                z = self._read_word_2c(REG_ZOUT_LSB)
                continue
            if status & STAT_DRDY:
                # Data is ready to read.
                x = self._read_word_2c(REG_XOUT_LSB)
                y = self._read_word_2c(REG_YOUT_LSB)
                z = self._read_word_2c(REG_ZOUT_LSB)
                t = self._read_word_2c(REG_TOUT_LSB)
                break
            else:
                # Waiting for DRDY.
                time.sleep(0.01)
                i += 1
        return [x, y, z, t]

    def get_magnet(self):
        """Get the 3 axis values from magnetic sensor."""
        [x, y, z, t] = self.get_data()
        return [x, y, z]

    def get_bearing(self):
        """Calculate horizontal bearing upon magnetic X and Y values."""
        [x, y, z, t] = self.get_data()
        if x is not None and y is not None:
            b = math.atan2(y, x)
            if b < 0:
                b += 2 * math.pi
            return math.degrees(b)
        else:
            return None

    def get_temp(self):
        """Get raw (uncalibrated) data from temperature sensor."""
        [x, y, z, t] = self.get_data()
        return t
