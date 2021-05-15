import matplotlib.pyplot as plt
import numpy as np
from pyrr import Vector4, Matrix44

from src.gui.plot import View

angle = 0

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.ion()

mV = View()
wV = View()
mV.scale(z=1/2, x=2, y=4)

while angle < 360:

    # View matrixes
    mV.rotateX(angle)
    wV.rotateY(angle)
    wV.translate(dx=1)
    angle+=50

    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.set_zlim([-5, 5])
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.set_zlabel("Z axis")

    # Original points
    points = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ])

    # Calculate normals
    deltaVec1, deltaVec2 = points[0] - points[1], points[0] - points[2]
    normal = np.cross(deltaVec1, deltaVec2)
    endPoints = points + normal


    # Compute new values
    worldPositions = []
    in_normal = None
    for i in range(len(points)):
        in_position = Vector4(np.concatenate([points[i],[1]]))
        in_normal = Vector4(normal.tolist() + [1])

        #GLSL
        worldMatrix = wV.translationMatrix * wV.rotationMatrix * wV.scaleMatrix
        modelMatrix = mV.translationMatrix * mV.scaleMatrix * mV.rotationMatrix
        matrix = worldMatrix * modelMatrix
        in_normal = (matrix.inverse.transpose() * in_normal)
        worldPosition = matrix * in_position

        #SAVE GLSL
        worldPositions.append(worldPosition.xyz)
        in_normal = in_normal.xyz

    # Plot original points and normals
    ax.plot_trisurf(points[:, 0], points[:, 1], points[:, 2], linewidth=0.2, antialiased=True)
    ax.quiver(
        points[:, 0], points[:, 1], points[:, 2],
        normal[0], normal[1], normal[2])
    ax.plot_trisurf(endPoints[:, 0], endPoints[:, 1], endPoints[:, 2], linewidth=0.2, antialiased=True)

    # Plot transformed points and normals
    worldPositions = np.array(worldPositions)
    in_normal = np.array(in_normal)
    in_normal /= np.linalg.norm(in_normal)
    endPoints = worldPositions + in_normal
    ax.plot_trisurf(worldPositions[:, 0], worldPositions[:, 1], worldPositions[:, 2], linewidth=0.2, antialiased=True)
    ax.quiver(
        worldPositions[:, 0], worldPositions[:, 1], worldPositions[:, 2],
        in_normal[0], in_normal[1], in_normal[2])
    ax.plot_trisurf(endPoints[:, 0], endPoints[:, 1], endPoints[:, 2], linewidth=0.2, antialiased=True)

    plt.show()
    plt.pause(0.1)

plt.pause(60)
