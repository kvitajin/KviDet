import cv2
from PIL import Image


class VideoLoader:
    def __init__(self):
        self._capture = cv2.VideoCapture()
        self._stop = False

    def load(self, video_or_webcam):
        if type(video_or_webcam) is int:
            self.load_webcam(video_or_webcam)
        else:
            self.load_video(video_or_webcam)

    def load_video(self, path: str):
        self._capture = cv2.VideoCapture(path)

    def load_webcam(self, id: int):
        self._capture = cv2.VideoCapture(id)

    def stop(self):
        self._stop = True

    def get_video_width(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    def get_video_height(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_video_frame_count(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def frames_as_pil(self):
        return map(Image.fromarray, self.frames())

    def frames(self):
        while self._capture.isOpened() and not self._stop:
            ret, frame = self._capture.read()

            if not ret:
                break

            frame_in_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            yield frame_in_rgb

        self._capture.release()