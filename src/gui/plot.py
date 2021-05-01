from typing import List

from pyrr import Matrix44, Quaternion, Vector3

from src.math.linalg import *
from src.math.space import Function
from OpenGL.GL import *
import pygalmesh

class Surface:
    def __init__(self, step, zoom):
        self.function = None
        self.name = None
        self.step = step
        self.zoom = zoom

        self.x = None
        self.y = None
        self.z = None
        self.zLog = None

        self.xZoom = None
        self.yZoom = None
        self.zZoom = None
        self.zZoomLog = None

        self.xMin = None
        self.yMin = None
        self.zMin = None
        self.zMinLog = None

        self.bounds = None
        self.zoomBounds = None

    def logZ(self, array):
        return np.log2(array - self.function.minValue + 1)

    def init(self, function: Function):
        self.function = function
        self.bounds = function.bounds
        self.name = function.name

        axes = [np.linspace(bound[0], bound[1], self.step).tolist() for bound in function.bounds]
        self.x, self.y = axes[0], axes[1]
        self.z = [[function(np.array([xi, yi])) for xi in self.x] for yi in self.y]
        self.zLog = self.logZ(self.z)

        XminDiff = abs(-function.bounds[0][0] + function.bounds[0][1]) / self.zoom
        YminDiff = abs(-function.bounds[1][0] + function.bounds[1][1]) / self.zoom
        self.zoomBounds = [
            [function.minVector[0][0] - XminDiff, function.minVector[0][0] + XminDiff],
            [function.minVector[0][1] - YminDiff, function.minVector[0][1] + YminDiff]
        ]
        Xaxe = np.linspace(*self.zoomBounds[0], self.step).tolist()
        Yaxe = np.linspace(*self.zoomBounds[1], self.step).tolist()
        self.xZoom, self.yZoom = Xaxe, Yaxe
        self.zZoom = [[function(np.array([xi, yi])) for xi in self.xZoom] for yi in self.yZoom]
        self.zZoomLog = self.logZ(self.zZoom)

        self.xMin = [o[0] for o in function.minVector]
        self.yMin = [o[1] for o in function.minVector]
        self.zMin = [function.minValue for _ in function.minVector]
        self.zMinLog = self.logZ(self.zMin)


class Shape:
    def __init__(self):
        self.colors: List[float] = []
        self.positions: List[float] = []
        self.normals: List[float] = []

    def __addGalMesh(self, mesh, color):
        for cell in mesh.cells:
            if cell.type == 'triangle':
                points, faces = mesh.points, cell.data
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

    def addSphere(self, position, radius, color):
        s = pygalmesh.Ball(position, radius)
        mesh = pygalmesh.generate_mesh(s, max_cell_circumradius=radius/5)
        self.__addGalMesh(mesh,color)

    def addTriangle(self):
        self.positions += [
            0, 0, 0,
            -1, 0, 0,
            0, 1, 0
        ]
        self.colors += [
            1,0,0,1,
            0,1,0,1,
            0,0,1,1,
        ]


class Scene:
    colorDim = 4
    positionDim = 3
    normalDim = 3

    def __init__(self):
        self.normalBuffer = None
        self.positionBuffer = None
        self.colorBuffer = None

        self.shapes: List[Shape] = []

        self.numVectors = 0
        self.posOffset = 0
        self.colOffset = 0
        self.norOffset = 0

    def initBuffers(self, maxNumVertexes=10 ** 5):
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
        glBufferSubData(GL_ARRAY_BUFFER, self.colOffset, normals)

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

class View:
    def __init__(self):
        self.rot_global_x = 0
        self.rot_local_z = 0
        self.globalLocation = [0, 0, 0]
        self.zoom = 1

    def rotate(self, global_x, local_z):
        self.rot_global_x += global_x
        self.rot_local_z += local_z

    def translate(self, dglobal_x=0, dglobal_y=0, dglobal_z=0):
        self.globalLocation[0] += dglobal_x
        self.globalLocation[1] += dglobal_y
        self.globalLocation[2] += dglobal_z

    def setZoom(self, zoom):
        self.zoom = zoom

    def projectionMatrix(self, width, height):
        return Matrix44.perspective_projection(45, width / height, 0.1, 100.0)

    def viewMatrix(self):
        scale = Vector3([self.zoom, self.zoom, self.zoom])
        translate = Vector3(self.globalLocation)

        mat = Matrix44.from_scale(scale)
        mat *= Matrix44.from_translation(translate)
        return mat

    def modelMatrix(self):
        zVector = Vector3([0, 0, 1])
        rotation = Quaternion.from_x_rotation(np.deg2rad(self.rot_global_x))
        zVector = rotation.matrix44 * zVector
        rotation *= Quaternion.from_axis_rotation(zVector, np.deg2rad(self.rot_local_z))
        rotation.normalize()

        return rotation.matrix44
