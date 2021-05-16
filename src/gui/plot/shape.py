from typing import List

import meshio
import numpy as np
import pygmsh

from src import utils
from src.optimization.space import Function


class Shape:

    def __init__(self):
        self.colors: List[float] = []
        self.positions: List[float] = []
        self.normals: List[float] = []

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

    def addLine(self, start: List[float], finish: List[float], color: List[float]):
        self.positions += start + finish
        self.colors += color + color
        self.normals += start + finish

    @staticmethod
    def Test(color):
        with pygmsh.occ.Geometry() as geom:
            cyl = geom.add_cylinder([0, 0, 0], [0, 0, 1], 1, mesh_size=0.1)
            cyl.id = cyl._id
            geom.force_outward_normals(cyl)
            mesh = geom.generate_mesh()

            shape = Shape()
            shape.__addMesh(mesh.points, mesh.cells[1].data, color)
            return shape

    @staticmethod
    def Cone(color):
        with pygmsh.occ.Geometry() as geom:
            cyl = geom.add_cone([0, 0, 0], [0, 0, 1], 1, 0, mesh_size=0.1)
            cyl.id = cyl._id
            geom.force_outward_normals(cyl)
            mesh = geom.generate_mesh()

            shape = Shape()
            shape.__addMesh(mesh.points, mesh.cells[1].data, color)
            return shape

    @staticmethod
    def Bunny(color):
        mesh = meshio.read(utils.getPath(__file__, '../../../data/models/bun_zipper.ply'))
        shape = Shape()
        shape.__addMesh(mesh.points, mesh.cells[0].data, color)
        return shape

    @staticmethod
    def Dragon(color):
        mesh = meshio.read(utils.getPath(__file__, '../../../data/models/dragon_vrip_res2.ply'))
        shape = Shape()
        shape.__addMesh(mesh.points, mesh.cells[0].data, color)
        return shape

    @staticmethod
    def Function(function: Function, step, color=(1, 1, 1, 1), zoomCenter: List[float] = None, zoom: float = 1):

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

        shape = Shape()
        shape.__addMesh(np.array(points, dtype=np.float32), np.array(faces, dtype=np.int32), color)
        return shape
