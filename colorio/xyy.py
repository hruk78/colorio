# -*- coding: utf-8 -*-
#
from __future__ import division

import matplotlib
import matplotlib.pyplot as plt
import numpy

from .illuminants import spectrum_to_xyz, planckian_radiator
from .srgb import SrgbLinear, SRGB1
from . import srgb


# pylint: disable=no-self-use
class XYY(object):
    def __init__(self):
        return

    def from_xyz(self, xyz):
        sum_xyz = numpy.sum(xyz, axis=0)
        x, y, _ = xyz
        return numpy.array([x/sum_xyz, y/sum_xyz, y])

    def to_xyz(self, xyy):
        x, y, Y = xyy
        return numpy.array([Y/y*x, Y, Y/y * (1-x-y)])

    def srgb_gamut(self, filename='srgb-xyy.vtu', n=50):
        srgb.show_gamut(filename, self.from_xyz, n=n, cut_000=True)
        return


def show_gamut_diagram(*args, **kwargs):
    plot_gamut_diagram(*args, **kwargs)
    plt.show()
    return


def partition(boxes, balls):
    # <https://stackoverflow.com/a/36748940/353337>
    def rec(boxes, balls, parent=tuple()):
        if boxes > 1:
            for i in range(balls + 1):
                for x in rec(boxes - 1, i, parent + (balls - i,)):
                    yield x
        else:
            yield parent + (balls,)

    return list(rec(boxes, balls))


def _plot_monochromatic():
    # draw outline of monochromatic spectra
    lmbda = 1.0e-9 * numpy.arange(380, 701)
    values = []
    # TODO vectorize (see <https://github.com/numpy/numpy/issues/10439>)
    for k, _ in enumerate(lmbda):
        data = numpy.zeros(len(lmbda))
        data[k] = 1.0
        values.append(XYY().from_xyz(spectrum_to_xyz((lmbda, data)))[:2])
    values = numpy.array(values)
    # fill horseshoe area
    plt.fill(values[:, 0], values[:, 1], color=[0.8, 0.8, 0.8], zorder=0)
    # plot horseshoe outline
    plt.plot(values[:, 0], values[:, 1], '-k', label='monochromatic light')
    return


def _plot_rgb_triangle():
    # plot sRGB triangle
    # discretization points
    n = 50

    # Get all RGB values that sum up to 1.
    rgb_linear = numpy.array(partition(3, n)).T / n
    # For the x-y-diagram, it doesn't matter if the values are scaled in any
    # way. After all, the tranlation to XYZ is linear, and then to xyY it's
    # (X/(X+Y+Z), Y/(X+Y+Z), Y), so the factor will only be present in the last
    # component which is discarded. To make the plot a bit brighter, scale the
    # colors up as much as possible.
    rgb_linear /= numpy.max(rgb_linear, axis=0)

    xyz = SrgbLinear().to_xyz(rgb_linear)
    xyy_vals = XYY().from_xyz(xyz)

    # Unfortunately, one cannot use tripcolors with explicit RGB specification
    # (see <https://github.com/matplotlib/matplotlib/issues/10265>). As a
    # workaround, associate range(n) data with the points and create a colormap
    # that associates the integer values with the respective RGBs.
    z = numpy.arange(xyy_vals.shape[1])
    rgb = SRGB1().from_srgb_linear(rgb_linear)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'gamut', rgb.T, N=len(rgb.T)
        )

    triang = matplotlib.tri.Triangulation(xyy_vals[0], xyy_vals[1])
    plt.tripcolor(triang, z, shading='gouraud', cmap=cmap)
    return


def _plot_planckian_locus():
    # plot planckian locus
    values = []
    for temp in numpy.arange(1000, 20001, 100):
        xyy_vals = XYY().from_xyz(spectrum_to_xyz(planckian_radiator(temp)))
        values.append(xyy_vals[:2])
    values = numpy.array(values)
    plt.plot(values[:, 0], values[:, 1], ':k', label='Planckian locus')
    return


def plot_gamut_diagram():
    _plot_monochromatic()
    _plot_rgb_triangle()
    _plot_planckian_locus()

    plt.xlim(xmin=0)
    plt.ylim(ymin=0)

    plt.gca().set_aspect('equal')
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    return