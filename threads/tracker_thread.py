from queue import Queue
from time import sleep
from typing import Dict

from tqdm import tqdm

from threads import QueueMessage, Task
from tracker import ObjectTracker


def tracker_thread(object_tracker: ObjectTracker, to_track: Queue, to_summarize: Queue, progressbar: tqdm):
    last_tracker_state = None

    while True:
        if object_tracker.stop:
            break

        if to_track.empty():
            sleep(1)
            continue

        task = to_track.get()

        if task.message == QueueMessage.DONE:
            break

        progressbar.update(1)
        detected_vehicles = task.payload
        last_tracker_state = object_tracker.track_objects(detected_vehicles)
        to_track.task_done()

    new_task = Task[Dict](payload=last_tracker_state)
    to_summarize.put(new_task)