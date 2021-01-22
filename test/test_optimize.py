import numpy as np
import pytest
from scipy.optimize import dual_annealing, minimize

import colorio


def dot(a, b):
    """Take arrays `a` and `b` and form the dot product between the last axis
    of `a` and the first of `b`.
    """
    b = np.asarray(b)
    return np.dot(a, b.reshape(b.shape[0], -1)).reshape(a.shape[:-1] + b.shape[1:])


class TestLab(colorio.cs.ColorSpace):
    def __init__(self, x):
        self.p = x[0]
        self.M1 = x[1:10].reshape(3, 3)
        self.M2 = x[10:19].reshape(3, 3)
        self.k0 = 0
        self.labels = ["L", "a", "b"]
        self.name = "TestLab"

    def from_xyz100(self, xyz):
        return dot(self.M2, dot(self.M1, xyz) ** self.p)

    def to_xyz100(self, xyz):
        self.M1inv = np.linalg.inv(self.M1)
        self.M2inv = np.linalg.inv(self.M2)
        return dot(self.M1inv, dot(self.M2inv, xyz) ** (1.0 / self.p))


@pytest.mark.skip
def test_optimize(maxiter=1):
    # luo_rigg = colorio.data.LuoRigg(8)
    bfd_p = colorio.data.BfdP()
    leeds = colorio.data.Leeds()
    macadam_1942 = colorio.data.MacAdam1942(Y=50)
    macadam_1974 = colorio.data.MacAdam1974()
    rit_dupont = colorio.data.RitDupont()
    witt = colorio.data.Witt()
    #
    ebner_fairchild = colorio.data.EbnerFairchild()
    hung_berns = colorio.data.HungBerns()
    xiao = colorio.data.Xiao()
    #
    munsell = colorio.data.Munsell()
    fairchild_chen = colorio.data.FairchildChen("SL2")

    def average(a, p):
        n = len(a)
        if p == 0:
            return np.prod(np.abs(a)) ** (1 / n)
        elif p == np.infty:
            return np.max(np.abs(a))
        return np.linalg.norm(a, p) / n ** (1 / p)

    def fun(x):
        cs = TestLab(x)
        d = np.array(
            [
                [1.0, bfd_p.stress(cs)],
                [1.0, leeds.stress(cs)],
                # [1.0, macadam_1942.stress(cs)],
                [1.0, macadam_1974.stress(cs)],
                [1.0, rit_dupont.stress(cs)],
                [1.0, witt.stress(cs)],
                #
                [0.1, average(ebner_fairchild.stress(cs), 3.0)],
                [0.4, average(hung_berns.stress(cs), np.infty)],
                [0.1, average(xiao.stress(cs), 3.0)],
                #
                [1.0, munsell.stress_lightness(cs)],
                [1.0, fairchild_chen.stress(cs)],
            ]
        )
        # make sure the weights add up to one
        d[:, 0] /= np.sum(d[:, 0])

        res = average(d[:, 0] * d[:, 1], 1.0)
        if np.isnan(res):
            res = 1.0e10
        # print(res)
        return res

    # np.random.seed(1)
    # x0 = np.random.rand(19)

    # x0 = np.array(
    #     [
    #         1.0 / 3.0,
    #         #
    #         0.8189330101, 0.3618667424, -0.1288597137,
    #         0.0329845436, 0.9293118715, 0.0361456387,
    #         0.0482003018, 0.2643662691, 0.6338517070,
    #         #
    #         0.2104542553, +0.7936177850, -0.0040720468,
    #         +1.9779984951, -2.4285922050, +0.4505937099,
    #         +0.0259040371, +0.7827717662, -0.8086757660,
    #     ]
    # )
    # x0 = np.array(
    #     [
    #         1.0,
    #         #
    #         1.0, 0.0, 0.0,
    #         0.0, 1.0, 0.0,
    #         0.0, 0.0, 1.0,
    #         #
    #         1.0, 0.0, 0.0,
    #         0.0, 1.0, 0.0,
    #         0.0, 0.0, 1.0,
    #     ]
    # )

    # print(fun(x0))

    # global search
    out = dual_annealing(
        fun,
        np.column_stack([np.full(19, -3.0), np.full(19, +3.0)]),
        # maxiter=maxiter
    )
    print("intermediate residual:")
    print(fun(out.x))
    # refine with bfgs
    out = minimize(
        fun,
        out.x,
        # method="Nelder-Mead",
        # method="Powell",
        # method="CG",
        method="BFGS",
        options={"maxiter": maxiter},
    )

    cs = TestLab(out.x)

    print()
    print("final residual:")
    print(fun(out.x))

    print()
    print("final values:")
    print(out.x[0])
    print(out.x[1:10].reshape(3, 3))
    print(out.x[10:19].reshape(3, 3))

    print()
    print("final residuals:")
    print("BFD-P.........", bfd_p.stress(cs))
    print("Leeds.........", leeds.stress(cs))
    print("MacAdam 1942..", macadam_1942.stress(cs))
    print("MacAdam 1974..", macadam_1974.stress(cs))
    print("RIT-DuPont....", rit_dupont.stress(cs))
    print("Witt..........", witt.stress(cs))
    print()
    print("Hung-Berns......", average(hung_berns.stress(cs), 1.0))
    print("EbnerFairchild..", average(ebner_fairchild.stress(cs), 1.0))
    print("Xiao............", average(xiao.stress(cs), 1.0))
    print()
    print("Munsell.........", munsell.stress_lightness(cs))
    print("FairchildChen...", fairchild_chen.stress(cs))

    cs.show_primary_srgb_gradients()
    macadam_1942.show(cs)
    macadam_1974.show(cs)
    hung_berns.show(cs)
    ebner_fairchild.show(cs)
    xiao.show(cs)
    fairchild_chen.show(cs)


if __name__ == "__main__":
    test_optimize(maxiter=100000)