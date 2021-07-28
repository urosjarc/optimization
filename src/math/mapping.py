import math

from hilbertcurve.hilbertcurve import HilbertCurve
from src.optimization.space import Function


def getPartitions(h, n):
    return round(math.log2(h+1)/n, 0)

def getPointFromProgress(hc: HilbertCurve, progress:float):
    p = list(hc.point_from_distance(progress*hc.max_h))
    for i in range(len(p)):
        p[i] = p[i]/float(hc.max_x)
    return p

def mappedPoint(point, axesRange):
    for i, ax in enumerate(point):
        ra = axesRange[i]
        point[i] = ra[0] + (ra[1] - ra[0])*ax

    return point

def mappedValue(hcFrom: HilbertCurve, hcTo: HilbertCurve, pointProg, fun: Function):
    hcPoint = mappedPoint(pointProg, [[0,e*hcFrom.max_x] for e in pointProg])
    progress = hcTo.distance_from_point(hcPoint) / hcTo.max_h
    pointND = getPointFromProgress(hcFrom, progress)
    mapPointND = mappedPoint(pointND, fun.bounds)
    return fun(mapPointND)
