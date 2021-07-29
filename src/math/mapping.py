import math

from hilbertcurve.hilbertcurve import HilbertCurve
from src.optimization.space import Function


def getPartitions(h, n):
    return round(math.log2(h+1)/n, 0)

def getProgressVectorFromProgress(hc: HilbertCurve, progress:float):
    p = list(hc.point_from_distance(progress*hc.max_h))
    for i in range(len(p)):
        p[i] = p[i]/float(hc.max_x)
    return p

def getHilbertPoint(progressVector, axesRange):
    for i, ax in enumerate(progressVector):
        ra = axesRange[i]
        progressVector[i] = ra[0] + (ra[1] - ra[0]) * ax

    return progressVector

def getProgressVector(vector, axesRange):
    for i, ax in enumerate(vector):
        ra = axesRange[i]
        vector[i] = (ax - ra[0])/(ra[1]-ra[0])

    return vector

def mappedPoint(hcFrom: HilbertCurve, hcTo: HilbertCurve, progressVector, bounds):
    hcPoint = getHilbertPoint(progressVector, [[0, e * hcFrom.max_x] for e in progressVector])
    progress = hcFrom.distance_from_point(hcPoint) / hcFrom.max_h
    progressVectorND= getProgressVectorFromProgress(hcTo, progress)
    return getHilbertPoint(progressVectorND, bounds)
