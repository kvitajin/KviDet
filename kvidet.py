from argparse import ArgumentParser
from queue import Queue
from threading import Thread
from time import sleep, time
from datetime import timedelta
from signal import signal, SIGINT

from tqdm import tqdm

import config as config_file
from threads import loader_thread, detector_thread, tracker_thread, Task, QueueMessage
from loader import VideoLoader


def kvidet(input_video, config):
    to_detect = Queue()
    to_track = Queue()
    to_summarize = Queue()

    video_loader = VideoLoader()
    video_loader.load(input_video)

    loader = Thread(target=loader_thread, args=(video_loader, to_detect), daemon=True)
    detector = Thread(target=detector_thread, args=(to_detect, to_track), daemon=True)
    tracker = Thread(target=tracker_thread, args=(to_track, to_summarize), daemon=True)

    # put terminating task on SIGTERM
    def stop_detection(sig, fr):
        terminating_task = Task(message=QueueMessage.DONE)
        video_loader.stop()
        to_detect.put(terminating_task)
        to_track.put(terminating_task)

    signal(SIGINT, stop_detection)

    loader.start()
    if not config.SILENT:
        print("loader started")

    detector.start()
    if not config.SILENT:
        print("detector started")

    tracker.start()
    if not config.SILENT:
        print("tracker started")

    if config.PROGRESS and not config.SILENT:
        print("-----------------")
        to_detect_bar = tqdm(desc="frames awaiting detection", total=video_loader.get_video_frame_count())
        to_track_bar = tqdm(desc="frames awaiting tracking", total=to_detect_bar.total)

        while to_summarize.empty():
            to_detect_bar.n = to_detect.qsize()
            to_track_bar.n = to_track.qsize()

            to_detect_bar.refresh()
            to_track_bar.refresh()

            sleep(2)

        to_detect_bar.close()
        to_track_bar.close()

    loader.join()
    if not config.SILENT:
        print("-----------------")
        print("loader finished")

    detector.join()
    if not config.SILENT:
        print("detector finished")

    tracker.join()
    if not config.SILENT:
        print("tracker finished")

    summarization_task = to_summarize.get()
    detected_vehicles = summarization_task.payload

    if not config.SILENT:
        print("-----------------")
        print("sorting vehicles by direction")

    sorted_vehicles_by_direction = {}
    for vehicle in detected_vehicles.values():
        for direction, bounding_vectors in config.BOUNDING_VECTORS.items():
            if direction not in sorted_vehicles_by_direction:
                sorted_vehicles_by_direction[direction] = []

            if len(vehicle.position_history) < 2:
                continue

            if vehicle.motion_vector.is_between(bounding_vectors[0], bounding_vectors[1]):
                sorted_vehicles_by_direction[direction].append(vehicle)
    return sorted_vehicles_by_direction


if __name__ == "__main__":
    arg_parser = ArgumentParser(description="Detekce projíždějících aut a jejich směrů")

    arg_parser.add_argument("input_path", help="cesta k videosouboru nebo číslo videokamery")
    arg_parser.add_argument("--silent", "-s", help="zda vypisovat na standardní výstup průběh detekce",
                            default=config_file.SILENT, action="store_true")
    arg_parser.add_argument("--debug", "-d", help="zda vypisovat ladící údaje na standardní výstup",
                            default=config_file.DEBUG, action="store_true")
    arg_parser.add_argument("--time", "-t", help="zda vypisovat na standardní výstup dobu strávenou detekcí",
                            default=config_file.TIME, action="store_true")
    arg_parser.add_argument("--progress", "-p", help="zda vypisovat živě průběh detekce na standardní výstup",
                            default=config_file.PROGRESS, action="store_true")

    args = arg_parser.parse_args()

    config = config_file
    config.SILENT = args.silent
    config.DEBUG = args.debug
    config.TIME = args.time
    config.PROGRESS = args.progress

    start_time = time()
    result = kvidet(args.input_path, config)
    end_time = time()

    print("-----------------")
    print("Results:")
    for direction in result:
        print(f"direction: {direction} vehicles: {len(result[direction])}")

    if config.TIME:
        elapsed_time=timedelta(seconds=end_time) - timedelta(seconds=start_time)
        hours, remainder = divmod(int(elapsed_time.total_seconds()), 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        print(f"elapsed time: {hours}h {minutes}m {seconds}s")