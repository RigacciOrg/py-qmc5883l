# Python driver for the QMC5883L 3-Axis Magnetic Sensor

Developed for the **Raspberry Pi**, requires the **python-smbus** package
to access the I2C bus.

Usage example:

```python
import qmc5883l
sensor = qmc5883l.QMC5883L()
m = sensor.get_magnet()
print(m)
```

The object constructor accepts some arguments, e.g. you can pass this one
to switch the output range to 8 Gauss, for very strong magnetic fields
which can otherwise overflow the sensor:

```python
sensor = qmc5883l.QMC5883L(output_range=qmc5883l.RNG_8G)
```

Read the Datasheet for other parameters.
