from typing import List

import meshio
import numpy as np
import pygmsh

from src import utils
from src.optimization.space import Function


class BoundBox:
    xMax = None
    xMin = None

    yMax = None
    yMin = None

    zMax = None
    zMin = None


class Shape:

    def __init__(self):
        self.colors: List[float] = []
        self.positions: List[float] = []
        self.normals: List[float] = []
        self.boundBox: BoundBox = BoundBox()

    @staticmethod
    def __boundBox(points):

        xMax, xMin = points[0][0], points[0][0]
        yMax, yMin = points[0][1], points[0][1]
        zMax, zMin = points[0][2], points[0][2]

        for i in range(len(points)):
            x = points[i][0]
            y = points[i][1]
            z = points[i][2]

            if x < xMin:
                xMin = x
            elif x > xMax:
                xMax = x

            if y < yMin:
                yMin = y
            elif y > yMax:
                yMax = y

            if z < zMin:
                zMin = z
            elif z > zMax:
                zMax = z

        return (xMax, xMin,
                yMax, yMin,
                zMax, zMin)

    def __addMesh(self, points, faces, color):
        norm = np.zeros(points.shape, dtype=points.dtype)
        tris = points[faces]
        n = np.cross(tris[::, 1] - tris[::, 0], tris[::, 2] - tris[::, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        for i in range(3):
            norm[faces[:, i]] += n
        norm /= np.linalg.norm(norm, axis=1, keepdims=True)
        va = points[faces]
        no = norm[faces]
        self.positions += va.ravel().tolist()
        self.normals += no.ravel().tolist()
        self.colors += np.tile(color, (faces.size, 1)).ravel().tolist()

        mM = self.__boundBox(points)
        self.boundBox.xMax = mM[0]
        self.boundBox.xMin = mM[1]
        self.boundBox.yMax = mM[2]
        self.boundBox.yMin = mM[3]
        self.boundBox.zMax = mM[4]
        self.boundBox.zMin = mM[5]
        return self

    def add_line(self, start: List[float], finish: List[float], color: List[float]):
        self.positions += start + finish
        self.colors += color + color
        self.normals += start + finish

    def add_test(self, color):
        with pygmsh.occ.Geometry() as geom:
            cyl = geom.add_cylinder([0, 0, 0], [0, 0, 1], 1, mesh_size=0.1)
            cyl.id = cyl._id
            geom.force_outward_normals(cyl)
            mesh = geom.generate_mesh()

            return self.__addMesh(mesh.points, mesh.cells[1].data, color)

    def add_cone(self, color):
        with pygmsh.occ.Geometry() as geom:
            cyl = geom.add_cone([0, 0, 0], [0, 0, 1], 1, 0, mesh_size=0.1)
            cyl.id = cyl._id
            geom.force_outward_normals(cyl)
            mesh = geom.generate_mesh()

            return self.__addMesh(mesh.points, mesh.cells[1].data, color)

    def add_bunny(self, color):
        mesh = meshio.read(utils.getPath(__file__, '../../../data/models/bun_zipper.ply'))
        return self.__addMesh(mesh.points, mesh.cells[0].data, color)

    def add_dragon(self, color):
        mesh = meshio.read(utils.getPath(__file__, '../../../data/models/dragon_vrip_res2.ply'))
        return self.__addMesh(mesh.points, mesh.cells[0].data, color)

    def add_function(self, function: Function, step, color=(1, 1, 1, 1), zoomCenter: List[float] = None,
                     zoom: float = 1):

        bounds = function.bounds
        if zoomCenter is not None and zoom != 1:
            xRange = abs(bounds[0][0] - bounds[0][1]) / zoom
            yRange = abs(bounds[1][0] - bounds[1][1]) / zoom
            bounds = [
                [max([bounds[0][0], zoomCenter[0] - xRange]), min([bounds[0][1], zoomCenter[0] + xRange])],
                [max([bounds[1][0], zoomCenter[1] - yRange]), min([bounds[1][1], zoomCenter[1] + yRange])]
            ]

        axis_x = np.linspace(*bounds[0], step)
        axis_y = np.linspace(*bounds[1], step)

        points = []
        faces = []

        sqC = 0  # Square count
        for yi in range(len(axis_y)):
            for xi in range(len(axis_x)):
                y = axis_y[yi]
                x = axis_x[xi]
                points.append([x, y, function([x, y])])
                upPoint = sqC + (len(axis_y))

                if xi < len(axis_x) - 1 and yi < len(axis_y) - 1:
                    faces += [
                        [sqC, sqC + 1, upPoint],
                        [sqC + 1, upPoint + 1, upPoint],
                    ]
                    sqC += 1
                else:
                    sqC += 1

        return self.__addMesh(np.array(points, dtype=np.float32), np.array(faces, dtype=np.int32), color)
