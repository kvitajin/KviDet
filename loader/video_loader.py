import cv2
from PIL import Image


class VideoLoader:
    def __init__(self):
        self._capture = cv2.VideoCapture()
    
    def load_video(self, path):
        self._capture = cv2.VideoCapture(path)
    
    def load_webcam(self, id):
        self._capture = cv2.VideoCapture(id)
    
    def get_video_width(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    def get_video_height(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
    def frames_as_pil(self):
        return map(Image.fromarray, self.frames())
    
    def frames(self):
        while self._capture.isOpened():
            ret, frame = self._capture.read()
            
            if not ret:
                break

            frame_in_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            yield frame_in_rgb

        self._capture.release()
