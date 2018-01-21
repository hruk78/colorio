# -*- coding: utf-8 -*-
#
from __future__ import division

import numpy

from .illuminants import white_point, d65
from . import srgb


class CIELUV(object):
    def __init__(self, whitepoint=white_point(d65())):
        self.whitepoint = whitepoint
        return

    def from_xyz(self, xyz):
        def f(t):
            delta = 6.0/29.0
            out = numpy.array(t, dtype=float)
            is_greater = out > delta**3
            out[is_greater] = 116*numpy.cbrt(out[is_greater]) - 16
            out[~is_greater] = out[~is_greater] / (delta/2)**3
            return out

        L = f(xyz[1]/self.whitepoint[1])

        x, y, z = xyz
        u = 4*x / (x + 15*y + 3*z)
        v = 9*y / (x + 15*y + 3*z)
        wx, wy, wz = self.whitepoint
        un = 4*wx / (wx + 15*wy + 3*wz)
        vn = 9*wy / (wx + 15*wy + 3*wz)
        return numpy.array([L, 13*L*(u - un), 13*L*(v - vn)])

    def to_xyz(self, luv):
        def f1(t):
            out = numpy.array(t, dtype=float)
            is_greater = out > 8
            out[is_greater] = ((out[is_greater]+16)/116)**3
            out[~is_greater] = out[~is_greater] * (3.0/29.0)**3
            return out

        L, u, v = luv

        wx, wy, wz = self.whitepoint
        un = 4*wx / (wx + 15*wy + 3*wz)
        vn = 9*wy / (wx + 15*wy + 3*wz)

        uu = u/(13*L) + un
        vv = v/(13*L) + vn

        Y = wy * f1(L)
        X = Y * 9*uu/(4*vv)
        Z = Y * (12 - 3*uu - 20*vv) / (4*vv)
        return numpy.array([X, Y, Z])

    def srgb_gamut(self, filename='srgb-cieluv.vtu', n=50):
        srgb.show_gamut(filename, self.from_xyz, n=n, cut_000=True)
        return