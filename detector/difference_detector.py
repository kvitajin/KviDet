import cv2
import numpy as np
from PIL import Image


class DifferenceDetector:
    def __init__(self):
        self._last_frame = None

    def difference_to_last_frame(self, frame: Image.Image):
        frame_in_gray = cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2GRAY)
        denoised_frame = cv2.fastNlMeansDenoising(frame_in_gray, None, 10, 7, 21)

        if self._last_frame is None:
            self._last_frame = denoised_frame
            return 1

        frame_diff = cv2.absdiff(self._last_frame, denoised_frame)
        frame_diff_as_int = frame_diff.astype(np.uint8)
        frame_diff_as_percentage = (np.count_nonzero(frame_diff_as_int) * 100) / frame_diff_as_int.size

        self._last_frame = denoised_frame

        return frame_diff_as_percentage / 100
