import numpy as np


def normalizeVector(vector):
    return vector / np.linalg.norm(vector)


def angle(v1, v2):
    v1_u = normalizeVector(v1)
    v2_u = normalizeVector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def pointInTriangle(pointVector, v1, v2, v3):
    sign = lambda p1, p2, p3: (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1 = sign(pointVector, v1, v2)
    d2 = sign(pointVector, v2, v3)
    d3 = sign(pointVector, v3, v1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0);
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0);
    return not (has_neg and has_pos)