# Python driver for the QMC5883L 3-Axis Magnetic Sensor

Developed for the **Raspberry Pi**, requires the **python-smbus** package
to access the I2C bus.

Usage example:

```python
import py_qmc5883l
sensor = py_qmc5883l.QMC5883L()
m = sensor.get_magnet()
print(m)
```

The object constructor accepts some arguments, e.g. you can pass this one to
switch the output range to 8 Gauss, for very strong magnetic fields which
can otherwise overflow the sensor:

```python
sensor = py_qmc5883l.QMC5883L(output_range=py_qmc5883l.RNG_8G)
```

The class constructor will initialize the sensor and put it into continuous
read mode, where a new reading is available into the registers at the Output
Data Rate (default is 10 Hz). To save power you can put the sensor in standby
mode calling the QMC5883L.mode_standby() method. To wakeup the sensor, just
call the QMC5883L.mode_continuous() once, and start getting values.

## Module installation

Installing from the source should be as simple as running:

```
python setup.py install
```

Make sure that the install destination directory exists, e.g. for the
Raspbian Stretch distro it is /usr/local/lib/python2.7/dist-packages.

## Documentation

Read the **[module source code](py_qmc5883l/__init__.py)** and the
**[chip Datasheet](doc/QMC5883L-Datasheet-1.0.pdf)**.
