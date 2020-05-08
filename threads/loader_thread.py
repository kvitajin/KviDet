from queue import Queue

from torch import Tensor

from detector import DifferenceDetector
from loader import VideoLoader, prepare_image_for_torch
import config
from threads import Task, QueueMessage


def loader_thread(video_or_webcam, to_detect: Queue):
    video_loader = VideoLoader()
    diff_detector = DifferenceDetector()

    if type(video_or_webcam) is int:
        video_loader.load_webcam(video_or_webcam)
    else:
        video_loader.load_video(video_or_webcam)

    for frame in video_loader.frames_as_pil():
        if diff_detector.difference_to_last_frame(frame) < config.MINIMUM_FRAME_DIFF:
            continue

        img_tensor = prepare_image_for_torch(frame)
        new_task = Task[Tensor](payload=img_tensor)
        to_detect.put(new_task)

    finishing_task = Task(message=QueueMessage.DONE)
    to_detect.put(finishing_task)
