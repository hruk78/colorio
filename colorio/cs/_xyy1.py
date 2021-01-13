import numpy

from .._exceptions import ColorioError
from ._color_space import ColorSpace


class XYY1(ColorSpace):
    """xyY colorspace with Y scaled from 0 to 1."""

    def __init__(self):
        super().__init__("xyY", ("x", "y", "Y"), 2, is_origin_well_defined=False)

    def from_xyz100(self, xyz100):
        if numpy.any(xyz100 < 0):
            raise ColorioError("Negative XYZ100 value.")

        xyz100 = numpy.asarray(xyz100)
        xyz = xyz100 / 100
        sum_xyz = numpy.sum(xyz, axis=0)
        x = xyz[0]
        y = xyz[1]
        return numpy.array([x / sum_xyz, y / sum_xyz, y])

    def to_xyz100(self, xyy):
        if numpy.any(xyy < 0):
            raise ColorioError("Negative xyY value.")
        x, y, Y = xyy
        return numpy.array([Y / y * x, Y, Y / y * (1 - x - y)]) * 100
