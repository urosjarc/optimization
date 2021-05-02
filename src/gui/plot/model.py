from OpenGL.GL import *

from typing import List

import meshio
import numpy as np
import pygmsh

from src import utils
from src.math.linalg import normalizeVectors

class Shape:
    def __init__(self):
        self.colors: List[float] = []
        self.positions: List[float] = []
        self.normals: List[float] = []

    def __addMesh(self, points, faces, color):
        norm = np.zeros(points.shape, dtype=points.dtype)
        tris = points[faces]
        n = np.cross(tris[::, 1] - tris[::, 0], tris[::, 2] - tris[::, 0])
        n = normalizeVectors(n)
        norm[faces[:, 0]] += n
        norm[faces[:, 1]] += n
        norm[faces[:, 2]] += n
        norm = normalizeVectors(norm)
        va = points[faces]
        no = norm[faces]
        va = va.ravel()
        no = no.ravel()
        self.positions += va.tolist()
        self.normals += no.tolist()
        self.colors += np.tile(color,(faces.size,1)).ravel().tolist()

    def addSquare(self, color):
        with pygmsh.geo.Geometry() as geom:
            poly = geom.add_polygon(
                [
                    [0.0, 0.0],
                    [1.0, -0.2],
                    [1.1, 1.2],
                    [0.1, 0.7],
                ],
                mesh_size=0.1,
            )
            geom.extrude(poly, [0.0, 0.3, 1.0], num_layers=5)
            mesh = geom.generate_mesh()
            self.__addMesh(mesh.points, mesh.cells[1].data, color)

    def addComplex(self, color):
        with pygmsh.occ.Geometry() as geom:
            geom.characteristic_length_max = 0.1
            ellipsoid = geom.add_ellipsoid([0.0, 0.0, 0.0], [1.0, 0.7, 0.5])

            cylinders = [
                geom.add_cylinder([-1.0, 0.0, 0.0], [2.0, 0.0, 0.0], 0.3),
                geom.add_cylinder([0.0, -1.0, 0.0], [0.0, 2.0, 0.0], 0.3),
                geom.add_cylinder([0.0, 0.0, -1.0], [0.0, 0.0, 2.0], 0.3),
            ]
            geom.boolean_difference(ellipsoid, geom.boolean_union(cylinders))

            mesh = geom.generate_mesh()
            self.__addMesh(mesh.points, mesh.cells[1].data, color)

    def addSphere(self, color):
        with pygmsh.geo.Geometry() as geom:
            geom.add_torus(1, 3, mesh_size=0.1)
            mesh = geom.generate_mesh()
            self.__addMesh(mesh.points, mesh.cells[1].data, color)

    def addBunny(self, color):
        mesh = meshio.read(utils.getPath(__file__, '../../../data/models/bun_zipper.ply'))
        self.__addMesh(mesh.points, mesh.cells[0].data, color)

    def addDragon(self, color):
        mesh = meshio.read(utils.getPath(__file__, '../../../data/models/dragon_vrip_res2.ply'))
        self.__addMesh(mesh.points, mesh.cells[0].data, color)


class Scene:
    colorDim = 4
    positionDim = 3
    normalDim = 3

    def __init__(self):
        self.normalBuffer = None
        self.positionBuffer = None
        self.colorBuffer = None

        self.numVectors = 0
        self.posOffset = 0
        self.colOffset = 0
        self.norOffset = 0

        self.shapes: List[Shape] = []

    def initBuffers(self, maxNumVertexes=10 ** 7):
        self.positionBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.positionBuffer)
        glBufferData(GL_ARRAY_BUFFER, np.empty(self.positionDim * maxNumVertexes, dtype=np.float32), GL_DYNAMIC_DRAW)

        self.colorBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.colorBuffer)
        glBufferData(GL_ARRAY_BUFFER, np.empty(self.colorDim * maxNumVertexes, dtype=np.float32), GL_DYNAMIC_DRAW)

        self.normalBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.normalBuffer)
        glBufferData(GL_ARRAY_BUFFER, np.empty(self.normalDim * maxNumVertexes, dtype=np.float32), GL_DYNAMIC_DRAW)

    def appendBuffers(self, shape: Shape):
        self.shapes.append(shape)
        positions = np.array(shape.positions, dtype=np.float32)
        colors = np.array(shape.colors, dtype=np.float32)
        normals = np.array(shape.normals, dtype=np.float32)

        posNum = positions.size // self.positionDim
        colNum = colors.size // self.colorDim
        norNum = normals.size // self.normalDim
        if posNum != colNum != norNum:
            raise Exception(f"Length of positions | colors | normals array doesn't match: {posNum} != {colNum}")

        glBindBuffer(GL_ARRAY_BUFFER, self.positionBuffer)
        glBufferSubData(GL_ARRAY_BUFFER, self.posOffset, positions)

        glBindBuffer(GL_ARRAY_BUFFER, self.colorBuffer)
        glBufferSubData(GL_ARRAY_BUFFER, self.colOffset, colors)

        glBindBuffer(GL_ARRAY_BUFFER, self.normalBuffer)
        glBufferSubData(GL_ARRAY_BUFFER, self.norOffset, normals)

        self.numVectors += posNum
        self.posOffset += positions.nbytes
        self.colOffset += colors.nbytes
        self.norOffset += normals.nbytes

    def setBuffers(self, shapes: List[Shape]):
        self.numVectors = 0
        self.posOffset = 0
        self.colOffset = 0
        self.norOffset = 0

        for shape in shapes:
            self.appendBuffers(shape)
