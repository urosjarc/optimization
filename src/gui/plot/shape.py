import copy
from typing import List

import meshio
import numpy as np
import pygmsh

from src import utils
from src.optimization.space import Function


class BoundBox:

    def __init__(self):
        self.start = []
        self.end = []
        self.dim = 0

    @staticmethod
    def calculate(points):
        b = BoundBox()
        b.dim = len(points[0])
        b.start = copy.deepcopy(points[0])
        b.end = copy.deepcopy(points[0])

        for i in range(len(points)):
            for axis in range(b.dim):
                axisLength = points[i][axis]
                if b.start[axis] > axisLength:
                    b.start[axis] = axisLength
                elif b.end[axis] < axisLength:
                    b.end[axis] = axisLength

        return b

    def resize(self, boundBox=None, points=None):
        bb = BoundBox.calculate(points) if points is not None else boundBox

        if not self.start:
            self.__dict__ = bb.__dict__
            return

        for axis in range(bb.dim):
            if bb.start[axis] < self.start[axis]:
                self.start[axis] = bb.start[axis]
            if bb.end[axis] > self.end[axis]:
                self.end[axis] = bb.end[axis]

    def center(self):
        return np.mean([self.end, self.start], axis=0)

class Shape:

    def __init__(self):
        self.colors: List[float] = []
        self.positions: List[float] = []
        self.normals: List[float] = []
        self.boundBox: BoundBox = BoundBox()

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

        self.boundBox.resize(points=points)

        return self

    def add_line(self, start: List[float], finish: List[float], color: List[float]):
        self.positions += start + finish
        self.colors += color + color
        self.normals += [0,0,0] + start #TODO: HERE IS WRITTEN WHICH POINT IS STARTING AND ENDING POINT :P
        self.boundBox.resize(points=[start, finish])
        return self

    def add_point(self, location: List[float], color: List[float]):
        self.positions += location
        self.colors += color
        self.normals += location
        self.boundBox.resize(points=[location])
        return self

    def add_boundBox(self, bb: BoundBox):
        color = [0, 0, 0, 1]
        p0 = [bb.xMin, bb.yMax, bb.zMax]
        p1 = [bb.xMax, bb.yMax, bb.zMax]
        p2 = [bb.xMax, bb.yMin, bb.zMax]
        p3 = [bb.xMin, bb.yMin, bb.zMax]
        p4 = [bb.xMin, bb.yMax, bb.zMin]
        p5 = [bb.xMax, bb.yMax, bb.zMin]
        p6 = [bb.xMax, bb.yMin, bb.zMin]
        p7 = [bb.xMin, bb.yMin, bb.zMin]

        #Up rectangle
        self.add_line(
            p0, p1, color
        ).add_line(
            p1, p2, color
        ).add_line(
            p2, p3, color
        ).add_line(
            p3, p0, color
        )

        #Down rectangle
        self.add_line(
            p4, p5, color
        ).add_line(
            p5, p6, color
        ).add_line(
            p6, p7, color
        ).add_line(
            p7, p4, color
        )

        #Up, down connection
        self.add_line(
            p0, p4, color
        ).add_line(
            p1, p5, color
        ).add_line(
            p2, p6, color
        ).add_line(
            p3, p7, color
        )

        #Diagonals

        self.add_line(
            p0, p6, color
        ).add_line(
            p1, p7, color
        ).add_line(
            p2, p4, color
        ).add_line(
            p3, p5, color
        )

        return self

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

    def add_cylinder(self, center, axis, radius, color):
        with pygmsh.occ.Geometry() as geom:
            cyl = geom.add_cylinder(center, axis, radius, mesh_size=0.1)
            cyl.id = cyl._id
            geom.force_outward_normals(cyl)
            mesh = geom.generate_mesh()

            return self.__addMesh(mesh.points, mesh.cells[1].data, color)

    def add_sphere(self, center, radius, color):
        with pygmsh.occ.Geometry() as geom:
            cyl = geom.add_ball(center, radius)
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
