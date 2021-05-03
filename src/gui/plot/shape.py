from typing import List

import meshio
import numpy as np
import pygmsh

from src import utils

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