from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


@dataclass
class BoundingBox:
    top_left: Point
    bottom_right: Point

    @property
    def center(self) -> Point:
        x_center = (self.top_left.x + self.bottom_right.x) / 2
        y_center = (self.top_left.y + self.bottom_right.y) / 2
        return Point(x=int(x_center), y=int(y_center))


@dataclass
class Vector(Point):
    def angle(self) -> float:
        in_radian = math.atan2(self.y, self.x)
        return math.degrees(in_radian)

    def is_between(self, vector_a: Vector, vector_b: Vector) -> bool:
        angle_a = vector_a.angle()
        angle_b = vector_b.angle()

        normalized_angle_a = normalize_angle(angle_a - self.angle())
        normalized_angle_b = normalize_angle(angle_b - self.angle())

        if (normalized_angle_a * normalized_angle_b) >=0:
            return False

        return math.fabs(normalized_angle_a - normalized_angle_b) < 180


def normalize_angle(angle):
    normalized_angle = angle
    while normalized_angle < -180:
        normalized_angle += 360
    while normalized_angle > 180:
        normalized_angle -= 360

    return normalized_angle


@dataclass
class Dimensions:
    width: int
    height: int