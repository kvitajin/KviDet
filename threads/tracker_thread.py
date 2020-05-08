from queue import Queue
from time import sleep
from typing import Dict

from threads import QueueMessage, Task
from tracker import ObjectTracker


def tracker_thread(to_track: Queue, to_summarize: Queue):
    tracker = ObjectTracker()
    last_tracker_state = None

    while True:
        if to_track.empty():
            sleep(1)
            continue

        task = to_track.get()

        if task.message == QueueMessage.DONE:
            break

        detected_vehicles = task.payload
        last_tracker_state = tracker.track_objects(detected_vehicles)
        to_track.task_done()

    new_task = Task[Dict](payload=last_tracker_state)
    to_summarize.put(new_task)
