from dataclasses import dataclass
from typing import List, Dict

import numpy as np

from detector import DetectedObject
from data.geometry import BoundingBox, Vector
from .sort.sort import Sort


@dataclass
class TrackedObject:
    id: int
    class_name: str
    position_history: List[BoundingBox]

    @property
    def motion_vector(self) -> Vector:
        if len(self.position_history) <= 1:
            return Vector(x=0, y=0)

        first_position = self.position_history[0]
        last_position = self.position_history[-1]
        vector_x = last_position.center.x - first_position.center.x
        vector_y = last_position.center.y - first_position.center.y

        return Vector(x=vector_x, y=vector_y)


def find_object_by_data(detected_objects: List[DetectedObject], raw_data: List):
    max_distance = 0.3  # TODO find a more robust solution

    for detected_object in detected_objects:
        distances = [
            abs(detected_object.raw_data[0] - raw_data[0]),
            abs(detected_object.raw_data[1] - raw_data[1]),
            abs(detected_object.raw_data[2] - raw_data[2]),
            abs(detected_object.raw_data[3] - raw_data[3])
        ]

        if all([distance < max_distance for distance in distances]):
            return detected_object

        return detected_object

    return None


class ObjectTracker:
    def __init__(self):
        self.stop = False

        self._mot_tracker = Sort()
        self._objects: Dict[TrackedObject] = {}

    def track_objects(self, detected_objects: List[DetectedObject]):
        detections = [d.raw_data for d in detected_objects]
        detections_as_array = np.array(detections)

        tracked_objects = self._mot_tracker.update(detections_as_array)

        for x1, y1, x2, y2, object_id in tracked_objects:
            detected_object = find_object_by_data(detected_objects,
                                                  [x1, y1, x2, y2])  # TODO find a more robust and performant solution

            if object_id not in self._objects:
                self._objects[object_id] = TrackedObject(id=object_id, class_name=detected_object.class_name,
                                                         position_history=[])

            self._objects[object_id].position_history.append(detected_object.bounding_box)

        return self._objects