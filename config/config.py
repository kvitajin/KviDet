from data.geometry import Vector

WEIGHTS_PATH: str = "weights/yolov3.weights"
CONFIDENCE_THRESHOLD = 0.8
NMS_THRESHOLD = 0.4
IMG_TARGET_SIZE = 416
MINIMUM_FRAME_DIFF = 1.5 / 100
SILENT = False
DEBUG = False
BOUNDING_VECTORS = {
    'LEFT': [
        Vector(x=-574, y=-189),
        Vector(x=-198, y=-134)
    ],
    'RIGHT': [
        Vector(x=472, y=462),
        Vector(x=416, y=141)
    ]
}
