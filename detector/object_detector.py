import os
from dataclasses import dataclass

import torch
from torch.autograd import Variable

from data.geometry import BoundingBox
from .yolo.models import Darknet
from .yolo.utils.utils import non_max_suppression, load_classes

import config


@dataclass
class DetectedObject:
    bounding_box: BoundingBox
    class_name: str
    raw_data: any


class ObjectDetector:
    def __init__(self):
        script_dir = os.path.dirname(__file__)

        self.stop = False

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor

        self._model = Darknet(os.path.join(script_dir, "yolo/config/yolov3.cfg")).to(self._device)
        self._classes = load_classes(os.path.join(script_dir, "yolo/data/coco.names"))

        if config.WEIGHTS_PATH.endswith(".weights"):
            self._model.load_darknet_weights(config.WEIGHTS_PATH)
        else:
            self._model.load_state_dict(torch.load(config.WEIGHTS_PATH))

        self._model.eval()

    def detect_in_image_tensor(self, image_tensor):
        input_image = Variable(image_tensor.type(self._Tensor))

        with torch.no_grad():
            detections = self._model(input_image)
            detections = non_max_suppression(detections, config.CONFIDENCE_THRESHOLD, config.NMS_THRESHOLD)

        return detections[0]