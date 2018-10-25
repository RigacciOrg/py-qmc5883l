#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate some pseudo-random points, aligned onto an ellipse."""

import numpy as np
import sys

A  = 3500.0  # Semi-axis A
B  = 2600.0  # Semi-axis B
Cx = -687.0  # Center Offset X
Cy = -1380.0  # Center Offset Y
perturb = 400.0  # Random error

# Ellipse rotation: a positive angle is counter-clockwise.
phi = np.pi * 0.22  # If phi < pi/4 then interpolated A > B
#phi = np.pi * 0.35  # Interpolated A < B

# Optional command-line argument range 0-100: means rotation 0-pi.
if len(sys.argv) > 1:
    phi = np.pi * (float(sys.argv[1]) / 100.0)

R = np.arange(0, 2*np.pi, 0.05)
x = A * np.cos(R) + Cx + perturb * np.random.rand(len(R))
y = B * np.sin(R) + Cy + perturb * np.random.rand(len(R))

# Rotate all points counter-clockwise around the ellipse center.
for i in range(0, len(x)):
    x1 = Cx + np.cos(phi) * (x[i] - Cx) - np.sin(phi) * (y[i] - Cy)
    y1 = Cy + np.sin(phi) * (x[i] - Cx) + np.cos(phi) * (y[i] - Cy)
    print("%f %f %f" % (x1, y1, 0))
