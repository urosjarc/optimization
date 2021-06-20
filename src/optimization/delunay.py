from typing import List
import numpy as np


class Point:
    def __init__(self, position):
        self.position = position
        self.x = position[0]
        self.y = position[1]

class Triangle:
    def __init__(self):
        self.points: List[Point] = []

    def contains(self, point: Point):
        '''
        https://math.stackexchange.com/questions/1226707/how-to-check-if-point-x-in-mathbbrn-is-in-a-n-simplex
        @param point:
        @return:
        '''
        upper = np.array([
            [0, [1,2,0], 0, 0],
            [1, 1, 2, 5],
            [1, 1, 1, -1],
            [1, 1, 2, 2]
        ])
        down = np.array([
            [1,2,5],
            [1,1,-1],
            [1,2,2]
        ])

        vec = -1 * np.linalg.det(upper) / np.linalg.det(down)


        print(vec)
        return True

class Mesh:
    def __init__(self):
        self.triangles: List[Triangle] = []

    def insert(self, position):
        point = Point(position)

        for triangle in self.triangles:
            if triangle.contains(point):
                print('huray')


if __name__ == '__main__':
    mesh = Mesh()
    triangle = Triangle()
    triangle.points = [
        Point([0,0]),
        Point([1,0]),
        Point([0,1])
    ]
    mesh.triangles.append(triangle)
    mesh.insert([.1,.1])
