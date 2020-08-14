from queue import Queue
from time import sleep

from tqdm import tqdm

from detector import ObjectDetector, DetectedObject
from data.geometry import Point, BoundingBox
from detector.yolo.utils.utils import load_classes
from threads import Task, QueueMessage


def detector_thread(object_detector: ObjectDetector, to_detect: Queue, to_track: Queue, progressbar: tqdm):
    classes = load_classes("detector/yolo/data/coco.names")

    while True:
        if object_detector.stop:
            break

        if to_detect.empty():
            sleep(1)
            continue

        task = to_detect.get()

        if task.message == QueueMessage.DONE:
            break

        progressbar.update(1)
        img_tensor = task.payload
        detections = object_detector.detect_in_image_tensor(img_tensor)

        detected_vehicles = []
        if detections is not None:
            for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:
                class_name = classes[int(cls_pred)]
                bounding_box = BoundingBox(top_left=Point(x=int(x1), y=int(y1)),
                                           bottom_right=Point(x=int(x2), y=int(y2)))
                raw_data = [x1, y1, x2, y2, conf]

                if class_name in ["car", "bus", "truck"]:
                    detected_vehicles.append(DetectedObject(bounding_box, class_name, raw_data))

        to_detect.task_done()

        if len(detected_vehicles) > 0:
            new_task = Task(payload=detected_vehicles)
            to_track.put(new_task)

    finishing_task = Task(message=QueueMessage.DONE)
    to_track.put(finishing_task)