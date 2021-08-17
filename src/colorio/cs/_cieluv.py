import numpy as np
from numpy.typing import ArrayLike

from ..illuminants import whitepoints_cie1931
from ._color_space import ColorSpace


class CIELUV(ColorSpace):
    def __init__(self, whitepoint: ArrayLike = whitepoints_cie1931["D65"]):
        super().__init__("CIELUV", ("L*", "u*", "v*"), 0, is_origin_well_defined=False)
        self.whitepoint_xyz100 = np.asarray(whitepoint)
        self.whitepoint = np.array([100.0, 0.0, 0.0])

    def from_xyz100(self, xyz: ArrayLike) -> np.ndarray:
        def f(t):
            delta = 6 / 29
            out = np.array(t, dtype=float)
            is_greater = out > delta ** 3
            out[is_greater] = 116 * np.cbrt(out[is_greater]) - 16
            out[~is_greater] = out[~is_greater] / (delta / 2) ** 3
            return out

        xyz = np.asarray(xyz)
        L = f(xyz[1] / self.whitepoint_xyz100[1])

        x, y, z = xyz
        p = x + 15 * y + 3 * z
        u = 4 * x / p
        v = 9 * y / p

        wx, wy, wz = self.whitepoint_xyz100
        q = wx + 15 * wy + 3 * wz
        un = 4 * wx / q
        vn = 9 * wy / q
        return np.array([L, 13 * L * (u - un), 13 * L * (v - vn)])

    def to_xyz100(self, luv: ArrayLike) -> np.ndarray:
        def f1(t):
            out = np.array(t, dtype=float)
            is_greater = out > 8
            out[is_greater] = ((out[is_greater] + 16) / 116) ** 3
            out[~is_greater] = out[~is_greater] * (3 / 29) ** 3
            return out

        L, u, v = np.asarray(luv)

        wx, wy, wz = self.whitepoint_xyz100
        q = wx + 15 * wy + 3 * wz
        un = 4 * wx / q
        vn = 9 * wy / q

        uu = u / (13 * L) + un
        vv = v / (13 * L) + vn

        Y = wy * f1(L)
        X = Y * 9 * uu / (4 * vv)
        Z = Y * (12 - 3 * uu - 20 * vv) / (4 * vv)
        return np.array([X, Y, Z])
