import unittest

from src.optimization.triangle import Point, Line, Triangle


class Test_Point(unittest.TestCase):
    def setUp(self):
        self.p1 = Point(0, 0, 0)
        self.p2 = Point(1, 1, 1)

    def test_distance(self):
        self.assertEqual(self.p1.distance(self.p2), 3 ** .5)
        self.assertEqual(self.p2.distance(self.p1), 3 ** .5)


class Test_Line(unittest.TestCase):
    def setUp(self):
        self.origin = Point(0, 0, 0)
        self.p1 = Point(1, 0, 0)
        self.line1 = Line(self.origin, self.p1)
        self.line2On1 = Line(Point(0.1, 0, 0), Point(0.9, 0, 0))
        self.lineNotOn1 = Line(Point(1, 0, 0), Point(2, 0, 0))
        self.line2 = Line(self.origin, Point(1, 1, 1))

    def test_attributes(self):
        self.assertEqual(self.origin.lines, [self.line1, self.line2])
        self.assertEqual(self.p1.lines, [self.line1])

    def test_size(self):
        self.assertEqual(self.line2.size(), 3 ** .5)

    def test_center(self):
        self.assertEqual(self.line2.center(), [.5, .5, .5])

    def test_mutualPoint(self):
        fakeOrigin = Point(0, 0, 0)
        self.assertEqual(self.line1.mutualPoint(self.line2), self.origin)
        self.assertNotEqual(self.line1.mutualPoint(self.line2), fakeOrigin)

    def test_isOnLine(self):
        fakeOrigin = Point(-10 ** -4, 0, 0)
        fakeOrigin1 = Point(-10 ** -6, 0, 0)
        self.assertTrue(self.line1.isOnLine(self.origin))
        self.assertFalse(self.line1.isOnLine(fakeOrigin))
        self.assertTrue(self.line1.isOnLine(fakeOrigin1))

    def test_coinciding(self):
        self.assertTrue(self.line1.coinciding(self.line2On1))
        self.assertTrue(self.line2On1.coinciding(self.line1))
        self.assertTrue(self.line1.coinciding(self.line1))
        self.assertFalse(self.line1.coinciding(self.lineNotOn1))
        self.assertFalse(self.lineNotOn1.coinciding(self.line1))


class Test_Triangle(unittest.TestCase):
    def setUp(self):
        self.p = [Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0)]
        self.p2 = [self.p[0], Point(1, 0, 3), Point(0, 1, 9)]
        self.lines = [
            Line(self.p[0], self.p[1]),
            Line(self.p[1], self.p[2]),
            Line(self.p[2], self.p[0])
        ]
        self.lines1 = [
            Line(self.p2[0], self.p2[1]),
            Line(self.p2[1], self.p2[2]),
            Line(self.p2[2], self.p2[0])
        ]
        self.tri1 = Triangle(self.lines)
        self.tri2 = Triangle([self.lines[0]])
        self.tri3 = Triangle(self.lines1)

    def test_attributes(self):
        self.assertEqual(len(set(self.tri1.points)), len(self.tri1.points))
        self.assertEqual(set(self.tri1.points), set(self.p))
        self.assertEqual(set(self.tri2.points), set([self.p[0], self.p[1]]))

        for i, p in enumerate(self.p):
            if i == 0:
                self.assertEqual(p.triangles, [self.tri1, self.tri2, self.tri3])
            elif i == 1:
                self.assertEqual(p.triangles, [self.tri1, self.tri2])
            else:
                self.assertEqual(p.triangles, [self.tri1])

    def test_meanValue(self):
        self.assertEqual(self.tri3.meanValue(), 4)

    def test_meanDiff(self):
        self.assertEqual(self.tri3.meanValueDiff(), 10)

    def test_lowestPoint(self):
        self.assertEqual(self.tri3.lowestPoint(), self.p2[0])

    def test_normalVector(self):
        self.assertEqual(self.tri1.normalVector().tolist(), [0, 0, .5])

    def test_fractureRatio(self):
        pass
        # self.assertWarns("Implement this!!!")

    def test_volume(self):
        self.assertEqual(self.tri1.volume(), 0.5)

    def test_sortedLines(self):
        self.assertEqual(self.tri1.sortedLines(fromBigToLow=True), [self.lines[1], self.lines[0], self.lines[2]])
        self.assertEqual(self.tri1.sortedLines(fromBigToLow=False), [self.lines[0], self.lines[2], self.lines[1]])

    def test_connectedTriangle(self):
        p = [Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0)]
        p1 = [p[0], p[2]] + [Point(-1, 0, 0)]
        p2 = [p[0], Point(-1, -1, 0), Point(1, -1, 0)]

        lines = [Line(p[0], p[1]), Line(p[1], p[2]), Line(p[2], p[0])]
        lines1 = [Line(p1[0], p1[1]), Line(p1[1], p1[2]), Line(p1[2], p1[0])]
        lines2 = [Line(p2[0], p2[1]), Line(p2[1], p2[2]), Line(p2[2], p2[0])]

        tri = Triangle(lines)
        tri1 = Triangle(lines1)
        tri2 = Triangle(lines2)

        self.assertEqual(tri.connectedTriangles(), [tri1])
        self.assertEqual(tri1.connectedTriangles(), [tri])
        self.assertEqual(tri2.connectedTriangles(), [])


if __name__ == '__main__':
    unittest.main()
