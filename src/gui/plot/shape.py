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

        if len(self.start) == 0:
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

    def __addMesh(self, points, faces, colors: List[List[float]]=None):
        norm = np.zeros(points.shape, dtype=points.dtype)
        tris = points[faces]
        n = np.cross(tris[::, 1] - tris[::, 0], tris[::, 2] - tris[::, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True)
        for i in range(3):
            norm[faces[:, i]] += n
        norm /= np.linalg.norm(norm, axis=1, keepdims=True)
        p = points[faces]
        n = norm[faces]
        self.positions += p.ravel().tolist()
        self.normals += n.ravel().tolist()

        if colors is not None:
            c = colors[faces]
            self.colors += c.ravel().tolist()
        else:
            self.colors += np.tile([1,1,1,1], (faces.size, 1)).ravel().tolist()

        self.boundBox.resize(points=points)

        return self

    def add_line(self, start: List[float], finish: List[float], color: List[float] = [1, 1, 1, 1]):
        self.positions += start + finish
        self.colors += color + color
        self.normals += [0, 0, 0] + start  # TODO: HERE IS WRITTEN WHICH POINT IS STARTING AND ENDING POINT :P
        self.boundBox.resize(points=[start, finish])
        return self

    def add_point(self, location: List[float], color: List[float] = [1, 1, 1, 1]):
        self.positions += location
        self.colors += color
        self.normals += location
        self.boundBox.resize(points=[location])
        return self

    def add_boundBox(self, bb: BoundBox):
        color = [0, 0, 0, 1]
        p0 = [bb.start[0], bb.end[1], bb.end[2]]
        p1 = [bb.end[0], bb.end[1], bb.end[2]]
        p2 = [bb.end[0], bb.start[1], bb.end[2]]
        p3 = [bb.start[0], bb.start[1], bb.end[2]]
        p4 = [bb.start[0], bb.end[1], bb.start[2]]
        p5 = [bb.end[0], bb.end[1], bb.start[2]]
        p6 = [bb.end[0], bb.start[1], bb.start[2]]
        p7 = [bb.start[0], bb.start[1], bb.start[2]]

        # Up rectangle
        self.add_line(
            p0, p1, color
        ).add_line(
            p1, p2, color
        ).add_line(
            p2, p3, color
        ).add_line(
            p3, p0, color
        )

        # Down rectangle
        self.add_line(
            p4, p5, color
        ).add_line(
            p5, p6, color
        ).add_line(
            p6, p7, color
        ).add_line(
            p7, p4, color
        )

        # Up, down connection
        self.add_line(
            p0, p4, color
        ).add_line(
            p1, p5, color
        ).add_line(
            p2, p6, color
        ).add_line(
            p3, p7, color
        )

        # Diagonals

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

    def add_function(self, function: Function, step, zoomCenter: List[float] = None, zoom=1):
        args = (function, step, zoomCenter, zoom)
        if function.dimensions == 1:
            return self.__add_function1D(*args)
        elif function.dimensions == 2:
            return self.__add_function2D(*args)
        elif function.dimensions == 3:
            return self.__add_function3D(*args)
        elif function.dimensions > 3:
            return self.__add_functionND(*args)

    def __add_function1D(self, function: Function, step, zoomCenter, zoom):
        bounds = function.bounds
        if zoomCenter is not None and zoom != 1:
            xRange = abs(bounds[0][0] - bounds[0][1]) / zoom
            bounds = [
                [max([bounds[0][0], zoomCenter[0] - xRange]), min([bounds[0][1], zoomCenter[0] + xRange])],
            ]
        axis_x = np.linspace(*bounds[0], step)
        points = []

        for xi in range(len(axis_x)):
            x = axis_x[xi]
            points.append([x, 0, function([x])])

        for i in range(len(points) - 1):
            self.add_line(points[i], points[i + 1])

        return self

    def __add_function2D(self, function: Function, step, zoomCenter, zoom):

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

        return self.__addMesh(np.array(points, dtype=np.float32), np.array(faces, dtype=np.int32))

    def __add_function3D(self, function: Function, step, zoomCenter, zoom):
        step = 2
        bounds = function.bounds
        if zoomCenter is not None and zoom != 1:
            xRange = abs(bounds[0][0] - bounds[0][1]) / zoom
            yRange = abs(bounds[1][0] - bounds[1][1]) / zoom
            zRange = abs(bounds[2][0] - bounds[2][1]) / zoom
            bounds = [
                [max([bounds[0][0], zoomCenter[0] - xRange]), min([bounds[0][1], zoomCenter[0] + xRange])],
                [max([bounds[1][0], zoomCenter[1] - yRange]), min([bounds[1][1], zoomCenter[1] + yRange])],
                [max([bounds[2][0], zoomCenter[2] - zRange]), min([bounds[2][1], zoomCenter[2] + zRange])]
            ]

        axis_x = np.linspace(*bounds[0], step)
        axis_y = np.linspace(*bounds[1], step)
        axis_z = np.linspace(*bounds[2], step)

        self.boundBox.resize(points=[[b[1] for b in bounds], [b[0] for b in bounds]])

        minVal = 10**10
        maxVal = -10**10

        for zi in range(len(axis_z)):
            for yi in range(len(axis_y)):
                for xi in range(len(axis_x)):
                    z = axis_z[zi]
                    y = axis_y[yi]
                    x = axis_x[xi]
                    val = function([x, y, z])
                    minVal = min([minVal, val])
                    maxVal = max([maxVal, val])

        valueScaling = lambda x, m, M: 1/(M-m) * (x-m)

        for zi in range(len(axis_z)-1):
            for yi in range(len(axis_y)-1):
                for xi in range(len(axis_x)-1):

                    x =  axis_x[xi]
                    y =  axis_y[yi]
                    z =  axis_z[zi]
                    x2 = axis_x[xi+1]
                    y2 = axis_y[yi+1]
                    z2 = axis_z[zi+1]

                    triangles = [
                        [0,1,2], [0,2,3],
                        [0,1,5], [0,5,4],
                        [0,4,6], [0,6,3]
                    ]
                    points = [
                        [x, y, z], [x2, y, z], [x2, y2, z], [x, y2, z],
                        [x, y, z2], [x2, y, z2], [x, y2, z2], [x2, y2, z2]
                    ]

                    # if xi+1 == len(axis_x)-1:
                    #     triangles += [[1,5,7], [1,2,7]]
                    # if yi+1 == len(axis_y)-1:
                    #     triangles += [[2,3,6], [2,6,7]]
                    # if zi+1 == len(axis_z)-1:
                    #     triangles += [[4,5,6], [5,6,7]]

                    values = [function(p) for p in points]

                    for tri in triangles:
                        for pi in tri:
                            self.positions += points[pi]
                            val = 0.5#valueScaling(values[pi], minVal, maxVal)
                            self.normals += [val] #this is a hack
                            self.colors += [1,1,1,1]


        return self

    def __add_functionND(self, function: Function, step, color, zoomCenter, zoom):
        pass
